#!/usr/bin/env python3
"""
Financial Data Ingestion Service for Sutra AI

This service orchestrates bulk ingestion of financial data from Google Sheets
into Sutra for semantic learning and temporal/causal reasoning.

Key capabilities:
- Google Sheets GOOGLEFINANCE function integration
- Bulk processing of historical stock data
- Semantic structuring for financial concepts
- Temporal relationship extraction
- Causal analysis support

Usage:
    python financial_ingester.py --config financial_config.json
    python financial_ingester.py --sheet-id "1ABC123..." --api-key "AIza..."
"""

import asyncio
import json
import logging
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import aiohttp
import pandas as pd
from tabulate import tabulate

# Add sutra packages to path
sys.path.append(str(Path(__file__).parent.parent / "sutra-core"))
sys.path.append(str(Path(__file__).parent.parent / "sutra-client"))

try:
    from sutra_core.core.storage_client import StorageClient
    from sutra_core.core.concept import Concept
    from sutra_client.client import SutraClient
except ImportError as e:
    print(f"Warning: Could not import Sutra modules: {e}")
    print("Running in standalone mode...")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FinancialConfig:
    """Configuration for financial data ingestion"""
    
    # Google Sheets configuration
    spreadsheet_id: str
    sheet_name: str = "FinancialData"
    range: str = "A1:Z10000"
    api_key: str = ""
    
    # Sutra configuration  
    sutra_api_url: str = "http://localhost:8000"
    sutra_storage_url: str = "localhost:7000"
    
    # Processing configuration
    batch_size: int = 100
    max_concepts_per_company: int = 1000
    enable_temporal_reasoning: bool = True
    enable_causal_analysis: bool = True
    
    # Company filter (empty = all companies)
    target_companies: List[str] = None
    
    # Date range filter
    start_date: Optional[str] = None  # YYYY-MM-DD
    end_date: Optional[str] = None    # YYYY-MM-DD

    def __post_init__(self):
        if self.target_companies is None:
            # Default to top AI/tech companies
            self.target_companies = [
                "NVDA", "GOOGL", "MSFT", "TSLA", "AAPL", "AMZN", "META",
                "NFLX", "CRM", "ORCL", "IBM", "INTC", "AMD", "QCOM",
                "ADBE", "NOW", "PLTR", "AI", "SNOW", "MDB"
            ]

class FinancialDataProcessor:
    """Processes financial data for Sutra semantic learning"""
    
    def __init__(self, config: FinancialConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.sutra_client: Optional[SutraClient] = None
        self.processed_concepts = 0
        self.failed_concepts = 0
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        
        # Initialize Sutra client
        try:
            self.sutra_client = SutraClient(
                api_url=self.config.sutra_api_url,
                storage_url=self.config.sutra_storage_url
            )
            await self.sutra_client.health_check()
            logger.info("Connected to Sutra successfully")
        except Exception as e:
            logger.warning(f"Could not connect to Sutra: {e}")
            logger.info("Running in test mode (no actual ingestion)")
            
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def fetch_financial_data(self) -> List[Dict[str, Any]]:
        """Fetch financial data from Google Sheets"""
        logger.info(f"Fetching data from Google Sheets: {self.config.spreadsheet_id}")
        
        url = (
            f"https://sheets.googleapis.com/v4/spreadsheets/{self.config.spreadsheet_id}"
            f"/values/{self.config.sheet_name}!{self.config.range}"
            f"?key={self.config.api_key}"
        )
        
        async with self.session.get(url) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Google Sheets API error ({response.status}): {error_text}")
                
            data = await response.json()
            
        values = data.get('values', [])
        if not values:
            logger.warning("No data found in the sheet")
            return []
            
        # Convert to list of dictionaries using first row as headers
        headers = values[0]
        financial_data = []
        
        for i, row in enumerate(values[1:], 1):
            # Pad row to match header length
            while len(row) < len(headers):
                row.append('')
                
            row_data = dict(zip(headers, row))
            row_data['source_row'] = i
            financial_data.append(row_data)
            
        logger.info(f"Loaded {len(financial_data)} rows of financial data")
        return financial_data
        
    def filter_financial_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter financial data based on configuration"""
        filtered_data = []
        
        for row in data:
            # Skip empty rows
            ticker = row.get('Ticker', '').strip().upper()
            if not ticker:
                continue
                
            # Filter by target companies
            if self.config.target_companies and ticker not in self.config.target_companies:
                continue
                
            # Filter by date range
            date_str = row.get('Date', '').strip()
            if date_str and self.config.start_date:
                try:
                    row_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    start_date = datetime.strptime(self.config.start_date, '%Y-%m-%d').date()
                    
                    if row_date < start_date:
                        continue
                        
                    if self.config.end_date:
                        end_date = datetime.strptime(self.config.end_date, '%Y-%m-%d').date()
                        if row_date > end_date:
                            continue
                            
                except ValueError:
                    logger.warning(f"Invalid date format: {date_str}")
                    continue
                    
            filtered_data.append(row)
            
        logger.info(f"Filtered to {len(filtered_data)} relevant data points")
        return filtered_data
        
    def create_financial_concepts(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert financial data to semantic concepts for Sutra"""
        concepts = []
        
        for row in data:
            ticker = row.get('Ticker', '').strip()
            date = row.get('Date', '').strip()
            
            if not ticker or not date:
                continue
                
            # Extract financial metrics
            price = self._safe_float(row.get('Price', ''))
            volume = self._safe_int(row.get('Volume', ''))
            market_cap = self._safe_float(row.get('Market Cap', ''))
            pe_ratio = self._safe_float(row.get('P/E Ratio', ''))
            dividend_yield = self._safe_float(row.get('Dividend Yield', ''))
            beta = self._safe_float(row.get('Beta', ''))
            
            # Create semantic content with temporal and causal context
            content_parts = [
                f"On {date}, {ticker} stock",
            ]
            
            metrics = []
            if price is not None:
                metrics.append(f"traded at ${price:.2f}")
            if volume is not None:
                metrics.append(f"with volume of {volume:,} shares")
            if market_cap is not None:
                metrics.append(f"market cap of ${market_cap/1e9:.1f}B")
            if pe_ratio is not None:
                metrics.append(f"P/E ratio of {pe_ratio:.1f}")
            if dividend_yield is not None:
                metrics.append(f"dividend yield of {dividend_yield*100:.2f}%")
            if beta is not None:
                metrics.append(f"beta of {beta:.2f}")
                
            if metrics:
                content_parts.append(", ".join(metrics))
                
            # Add temporal context for Sutra's temporal reasoning
            try:
                parsed_date = datetime.strptime(date, '%Y-%m-%d')
                weekday = parsed_date.strftime('%A')
                month = parsed_date.strftime('%B')
                year = parsed_date.year
                
                content_parts.append(f"This was on a {weekday} in {month} {year}")
                
                # Add relative temporal context
                today = datetime.now()
                days_ago = (today - parsed_date).days
                if days_ago < 7:
                    content_parts.append(f"which was {days_ago} days ago")
                elif days_ago < 365:
                    weeks_ago = days_ago // 7
                    content_parts.append(f"which was {weeks_ago} weeks ago")
                else:
                    years_ago = days_ago // 365
                    content_parts.append(f"which was {years_ago} years ago")
                    
            except ValueError:
                pass
                
            # Create rich semantic content
            semantic_content = ". ".join(content_parts) + "."
            
            # Add causal context if enabled
            if self.config.enable_causal_analysis:
                causal_context = self._generate_causal_context(ticker, price, volume, date)
                if causal_context:
                    semantic_content += f" {causal_context}"
            
            # Create concept
            concept = {
                "content": semantic_content,
                "metadata": {
                    "ticker": ticker,
                    "date": date,
                    "price": price,
                    "volume": volume,
                    "market_cap": market_cap,
                    "pe_ratio": pe_ratio,
                    "dividend_yield": dividend_yield,
                    "beta": beta,
                    "domain": "finance",
                    "entity_type": "stock_data",
                    "data_source": "google_sheets",
                    "source_row": row.get('source_row'),
                    
                    # Temporal metadata for advanced reasoning
                    "year": parsed_date.year if 'parsed_date' in locals() else None,
                    "month": parsed_date.month if 'parsed_date' in locals() else None,
                    "day": parsed_date.day if 'parsed_date' in locals() else None,
                    "weekday": parsed_date.weekday() if 'parsed_date' in locals() else None,
                    
                    # Classification metadata for Sutra's semantic understanding
                    "concept_type": "quantitative",  # Sutra's 9 semantic types
                    "temporal_type": "point_in_time",
                    "causal_relevance": "market_data",
                }
            }
            
            concepts.append(concept)
            
        logger.info(f"Created {len(concepts)} semantic concepts from financial data")
        return concepts
        
    def _safe_float(self, value: str) -> Optional[float]:
        """Safely convert string to float"""
        if not value or value.strip() == '':
            return None
        try:
            # Handle common formatting (commas, currency symbols, percentages)
            cleaned = value.replace(',', '').replace('$', '').replace('%', '').replace('B', '000000000').replace('M', '000000')
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
            
    def _safe_int(self, value: str) -> Optional[int]:
        """Safely convert string to int"""
        if not value or value.strip() == '':
            return None
        try:
            cleaned = value.replace(',', '')
            return int(float(cleaned))  # Handle decimal integers
        except (ValueError, AttributeError):
            return None
            
    def _generate_causal_context(self, ticker: str, price: Optional[float], 
                               volume: Optional[int], date: str) -> str:
        """Generate causal context for enhanced reasoning"""
        causal_statements = []
        
        # Price-based causal reasoning
        if price is not None:
            if price > 1000:
                causal_statements.append(f"High stock price of ${price:.2f} may indicate strong investor confidence in {ticker}")
            elif price < 10:
                causal_statements.append(f"Low stock price of ${price:.2f} may indicate market concerns about {ticker}")
                
        # Volume-based causal reasoning  
        if volume is not None and volume > 50000000:  # High volume
            causal_statements.append(f"High trading volume of {volume:,} shares suggests significant market interest")
            
        # Temporal causal reasoning
        try:
            parsed_date = datetime.strptime(date, '%Y-%m-%d')
            
            # Market timing effects
            if parsed_date.weekday() == 0:  # Monday
                causal_statements.append("Monday trading may be influenced by weekend news")
            elif parsed_date.weekday() == 4:  # Friday
                causal_statements.append("Friday trading may be affected by week-end position adjustments")
                
            # Quarterly effects
            if parsed_date.month in [3, 6, 9, 12] and parsed_date.day > 20:
                causal_statements.append("End-of-quarter timing may influence trading patterns")
                
        except ValueError:
            pass
            
        return " ".join(causal_statements)
        
    async def bulk_ingest_concepts(self, concepts: List[Dict[str, Any]]) -> Dict[str, int]:
        """Bulk ingest concepts into Sutra"""
        if not self.sutra_client:
            logger.warning("No Sutra client available - simulating ingestion")
            return {"processed": len(concepts), "failed": 0}
            
        results = {"processed": 0, "failed": 0}
        
        # Process in batches for efficiency
        for i in range(0, len(concepts), self.config.batch_size):
            batch = concepts[i:i + self.config.batch_size]
            
            try:
                # Convert to Sutra concepts
                sutra_concepts = []
                for concept_data in batch:
                    sutra_concept = Concept(
                        content=concept_data["content"],
                        metadata=concept_data["metadata"]
                    )
                    sutra_concepts.append(sutra_concept)
                    
                # Bulk learn via Sutra API
                concept_ids = await self.sutra_client.learn_concepts(sutra_concepts)
                results["processed"] += len(concept_ids)
                
                logger.info(f"Processed batch {i//self.config.batch_size + 1}: {len(concept_ids)} concepts")
                
            except Exception as e:
                logger.error(f"Failed to process batch {i//self.config.batch_size + 1}: {e}")
                results["failed"] += len(batch)
                
        self.processed_concepts = results["processed"]
        self.failed_concepts = results["failed"]
        
        return results
        
    async def run_ingestion(self) -> Dict[str, Any]:
        """Run complete financial data ingestion pipeline"""
        logger.info("Starting financial data ingestion pipeline")
        start_time = datetime.now()
        
        try:
            # Step 1: Fetch data from Google Sheets
            raw_data = await self.fetch_financial_data()
            
            # Step 2: Filter and clean data
            filtered_data = self.filter_financial_data(raw_data)
            
            # Step 3: Create semantic concepts
            concepts = self.create_financial_concepts(filtered_data)
            
            # Step 4: Bulk ingest into Sutra
            results = await self.bulk_ingest_concepts(concepts)
            
            # Calculate metrics
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            concepts_per_second = results["processed"] / processing_time if processing_time > 0 else 0
            
            summary = {
                "status": "success",
                "raw_rows": len(raw_data),
                "filtered_rows": len(filtered_data),
                "concepts_created": len(concepts),
                "concepts_ingested": results["processed"],
                "concepts_failed": results["failed"],
                "processing_time_seconds": processing_time,
                "concepts_per_second": concepts_per_second,
                "companies_processed": len(set(row.get('Ticker', '') for row in filtered_data)),
                "date_range": {
                    "start": self.config.start_date,
                    "end": self.config.end_date
                }
            }
            
            logger.info("Financial data ingestion completed successfully")
            logger.info(f"Processed {results['processed']} concepts in {processing_time:.1f}s ({concepts_per_second:.1f} concepts/sec)")
            
            return summary
            
        except Exception as e:
            logger.error(f"Financial data ingestion failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "processed_concepts": self.processed_concepts,
                "failed_concepts": self.failed_concepts
            }

def create_sample_config() -> FinancialConfig:
    """Create sample configuration for testing"""
    return FinancialConfig(
        spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",  # Example sheet
        sheet_name="FinancialData",
        range="A1:H1000",
        api_key="YOUR_GOOGLE_API_KEY_HERE",
        target_companies=["NVDA", "GOOGL", "MSFT", "TSLA", "AAPL"],
        start_date="2024-01-01",
        end_date="2025-11-07",
        batch_size=50,
        enable_temporal_reasoning=True,
        enable_causal_analysis=True
    )

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Financial Data Ingestion for Sutra AI")
    parser.add_argument("--config", type=str, help="Configuration JSON file")
    parser.add_argument("--sheet-id", type=str, help="Google Sheets ID")
    parser.add_argument("--api-key", type=str, help="Google API key")
    parser.add_argument("--companies", type=str, help="Comma-separated list of ticker symbols")
    parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--sample-config", action="store_true", help="Generate sample configuration")
    parser.add_argument("--dry-run", action="store_true", help="Test configuration without ingesting")
    
    args = parser.parse_args()
    
    if args.sample_config:
        config = create_sample_config()
        print(json.dumps(asdict(config), indent=2))
        return
        
    # Load configuration
    if args.config:
        with open(args.config, 'r') as f:
            config_dict = json.load(f)
        config = FinancialConfig(**config_dict)
    else:
        config = create_sample_config()
        
    # Override with command line arguments
    if args.sheet_id:
        config.spreadsheet_id = args.sheet_id
    if args.api_key:
        config.api_key = args.api_key
    if args.companies:
        config.target_companies = [c.strip().upper() for c in args.companies.split(',')]
    if args.start_date:
        config.start_date = args.start_date
    if args.end_date:
        config.end_date = args.end_date
        
    # Validate configuration
    if not config.api_key or config.api_key == "YOUR_GOOGLE_API_KEY_HERE":
        print("Error: Google API key is required")
        print("Get your API key from: https://console.cloud.google.com/apis/credentials")
        return
        
    if not config.spreadsheet_id:
        print("Error: Google Sheets ID is required")
        return
        
    # Run ingestion
    async with FinancialDataProcessor(config) as processor:
        if args.dry_run:
            logger.info("Dry run mode - testing configuration...")
            try:
                data = await processor.fetch_financial_data()
                filtered = processor.filter_financial_data(data)
                concepts = processor.create_financial_concepts(filtered)
                
                print(f"Configuration test successful:")
                print(f"  Raw data rows: {len(data)}")
                print(f"  Filtered rows: {len(filtered)}")
                print(f"  Concepts created: {len(concepts)}")
                print(f"  Sample concept:")
                if concepts:
                    print(f"    Content: {concepts[0]['content'][:100]}...")
                    
            except Exception as e:
                print(f"Configuration test failed: {e}")
        else:
            result = await processor.run_ingestion()
            print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())