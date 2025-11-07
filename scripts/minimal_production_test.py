#!/usr/bin/env python3
"""
Minimal test replicating production script logic
"""

import requests
import json
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import random
import time

@dataclass
class CompanyConfig:
    ticker: str
    name: str
    sector: str
    priority: str
    market_cap_billions: float

class MinimalProductionTest:
    def __init__(self):
        self.base_url = "http://localhost:8080/api"
        self.session = requests.Session()
        self.retry_attempts = 3
        self.retry_delay = 1
    
    def create_financial_concept(self, company: CompanyConfig, date: datetime) -> Dict[str, Any]:
        """Create realistic financial concept - exactly like production script"""
        # Realistic price generation
        base_prices = {
            "AAPL": 180.0, "MSFT": 380.0, "GOOGL": 140.0, "AMZN": 145.0, "NVDA": 450.0,
            "TSLA": 220.0, "META": 320.0, "NFLX": 480.0, "ADBE": 580.0, "CRM": 250.0
        }
        
        base_price = base_prices.get(company.ticker, 100.0)
        daily_volatility = random.uniform(0.01, 0.05)
        price_change = random.uniform(-daily_volatility, daily_volatility)
        
        open_price = round(base_price * (1 + random.uniform(-0.02, 0.02)), 2)
        close_price = round(open_price * (1 + price_change), 2)
        high_price = round(max(open_price, close_price) * (1 + random.uniform(0, 0.03)), 2)
        low_price = round(min(open_price, close_price) * (1 - random.uniform(0, 0.02)), 2)
        volume = random.randint(int(company.market_cap_billions * 1000000), int(company.market_cap_billions * 5000000))
        
        daily_change = close_price - open_price
        daily_change_pct = (daily_change / open_price) * 100
        volatility = ((high_price - low_price) / open_price) * 100
        
        return {
            "content": f"{company.name} ({company.ticker}) financial data for {date.strftime('%Y-%m-%d')}: "
                      f"Stock opened at ${open_price:.2f}, closed at ${close_price:.2f}, "
                      f"with high of ${high_price:.2f} and low of ${low_price:.2f}. "
                      f"Trading volume was {volume:,} shares. Daily change: {daily_change:+.2f} ({daily_change_pct:+.2f}%). "
                      f"Market volatility: {volatility:.2f}%. Sector: {company.sector}. "
                      f"Market cap: ${company.market_cap_billions:.1f}B.",
            "metadata": {
                "source": "financial_market_data",
                "company": company.ticker,
                "company_name": company.name,
                "sector": company.sector,
                "date": date.strftime('%Y-%m-%d'),
                "data_type": "daily_ohlcv",
                "price_open": str(open_price),
                "price_close": str(close_price),
                "price_high": str(high_price),
                "price_low": str(low_price),
                "volume": str(volume),
                "daily_change": str(round(daily_change, 2)),
                "daily_change_pct": str(round(daily_change_pct, 2)),
                "volatility": str(round(volatility, 2)),
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def ingest_concept_with_retry(self, concept: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
        """Ingest concept with retry - exactly like production script"""
        for attempt in range(self.retry_attempts):
            try:
                print(f"    📡 Attempt {attempt + 1}: Posting to {self.base_url}/learn")
                response = self.session.post(f"{self.base_url}/learn", json=concept, timeout=30)
                
                print(f"    📡 Response: {response.status_code} - {response.text[:100]}")
                
                if response.status_code == 201:
                    result = response.json()
                    concept_id = result.get("concept_id", "unknown")
                    print(f"    ✅ Success! Concept ID: {concept_id}")
                    return True, concept_id, None
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    print(f"    ❌ HTTP Error: {error_msg}")
                    if attempt == self.retry_attempts - 1:
                        return False, None, error_msg
                    time.sleep(self.retry_delay * (2 ** attempt))
                    
            except Exception as e:
                error_msg = f"Request failed: {str(e)}"
                print(f"    💥 Exception: {error_msg}")
                if attempt == self.retry_attempts - 1:
                    return False, None, error_msg
                time.sleep(self.retry_delay * (2 ** attempt))
        
        print(f"    ❌ Max retries exceeded")
        return False, None, "Max retry attempts exceeded"
    
    def test_company_data_ingestion(self, ticker: str = "AAPL", days: int = 3):
        """Test company data ingestion - exactly like production script"""
        print(f"🧪 Testing {ticker} data ingestion for {days} days")
        
        company = CompanyConfig(
            ticker=ticker,
            name="Apple Inc",
            sector="Technology",
            priority="HIGH",
            market_cap_billions=3000.0
        )
        
        results = {
            "company": company.ticker,
            "success_count": 0,
            "failure_count": 0,
            "concept_ids": [],
            "errors": []
        }
        
        start_date = datetime.now() - timedelta(days=days)
        
        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)
            
            # Skip weekends
            if current_date.weekday() >= 5:
                print(f"  📅 Skipping {current_date.strftime('%Y-%m-%d %A')} (weekend)")
                continue
            
            print(f"  📅 Processing {current_date.strftime('%Y-%m-%d %A')}")
            
            concept = self.create_financial_concept(company, current_date)
            success, concept_id, error = self.ingest_concept_with_retry(concept)
            
            if success:
                results["success_count"] += 1
                results["concept_ids"].append(concept_id)
                print(f"  ✅ Success: {concept_id}")
            else:
                results["failure_count"] += 1
                results["errors"].append(f"{current_date.strftime('%Y-%m-%d')}: {error}")
                print(f"  ❌ Failed: {error}")
        
        print(f"\n📊 Results for {ticker}:")
        print(f"  Success: {results['success_count']}")
        print(f"  Failures: {results['failure_count']}")
        print(f"  Concept IDs: {results['concept_ids']}")
        print(f"  Errors: {results['errors']}")
        
        return results

def main():
    print("🧪 MINIMAL PRODUCTION TEST")
    print("=" * 50)
    
    tester = MinimalProductionTest()
    
    # Test with a small dataset
    results = tester.test_company_data_ingestion("AAPL", 5)
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"Success Rate: {results['success_count']}/{results['success_count'] + results['failure_count']}")
    print(f"Concepts Created: {results['success_count']}")
    
    if results['success_count'] > 0:
        print("✅ Production script logic is working!")
    else:
        print("❌ Something is wrong with the production script logic.")

if __name__ == "__main__":
    main()