#!/usr/bin/env python3
"""
MSME Bulk Ingester Plugin
Adapter for processing Government of India MSME data through Sutra's bulk ingestion system

This demonstrates how to create a plugin for sutra-bulk-ingester to handle
specific data formats while following the unified learning pipeline.
"""

import json
import csv
import asyncio
from typing import Dict, Any, List, Iterator, Optional
from pathlib import Path
import aiofiles
from datetime import datetime

class MSMEAdapter:
    """Adapter for MSME data ingestion into Sutra bulk ingester"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "msme_csv_adapter"
        self.version = "1.0.0"
        self.supported_formats = ["csv", "json", "xlsx"]
    
    async def validate_source(self, source_config: Dict[str, Any]) -> bool:
        """Validate that the data source is accessible and properly formatted"""
        
        source_type = source_config.get("source_type", "")
        
        if source_type == "csv":
            csv_path = Path(source_config.get("csv_path", ""))
            if not csv_path.exists():
                raise FileNotFoundError(f"CSV file not found: {csv_path}")
            
            # Validate CSV has required columns
            required_columns = [
                "udyam_number", "enterprise_name", "state", "district",
                "nic_code", "category", "investment_in_plant", "annual_turnover"
            ]
            
            async with aiofiles.open(csv_path, 'r', encoding='utf-8') as f:
                first_line = await f.readline()
                headers = [col.strip().lower() for col in first_line.split(',')]
                
                missing_columns = [col for col in required_columns if col not in headers]
                if missing_columns:
                    raise ValueError(f"Missing required columns: {missing_columns}")
            
            return True
        
        elif source_type == "api":
            # Validate API endpoint is accessible
            api_url = source_config.get("api_url", "")
            api_key = source_config.get("api_key", "")
            
            if not api_url:
                raise ValueError("API URL is required")
            
            # Test API connectivity (implementation would ping the endpoint)
            return True
        
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
    
    async def estimate_total_items(self, source_config: Dict[str, Any]) -> Optional[int]:
        """Estimate total number of items to be processed"""
        
        source_type = source_config.get("source_type", "")
        
        if source_type == "csv":
            csv_path = Path(source_config.get("csv_path", ""))
            
            line_count = 0
            async with aiofiles.open(csv_path, 'r', encoding='utf-8') as f:
                async for line in f:
                    line_count += 1
            
            return max(0, line_count - 1)  # Subtract header row
        
        elif source_type == "api":
            # For API sources, we might query a count endpoint
            return None  # Unknown until we start processing
        
        return None
    
    async def stream_data(self, source_config: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Stream MSME data records for processing"""
        
        source_type = source_config.get("source_type", "")
        
        if source_type == "csv":
            async for record in self._stream_csv_data(source_config):
                yield record
        
        elif source_type == "api":
            async for record in self._stream_api_data(source_config):
                yield record
        
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
    
    async def _stream_csv_data(self, source_config: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Stream data from CSV file"""
        
        csv_path = Path(source_config.get("csv_path", ""))
        encoding = source_config.get("encoding", "utf-8")
        chunk_size = source_config.get("chunk_size", 1000)
        
        async with aiofiles.open(csv_path, 'r', encoding=encoding) as f:
            # Read header
            header_line = await f.readline()
            headers = [col.strip() for col in header_line.strip().split(',')]
            
            batch = []
            async for line in f:
                if line.strip():
                    values = [val.strip().strip('"') for val in line.strip().split(',')]
                    record = dict(zip(headers, values))
                    
                    # Transform to standard MSME format
                    msme_record = self._transform_csv_record(record)
                    batch.append(msme_record)
                    
                    if len(batch) >= chunk_size:
                        for item in batch:
                            yield item
                        batch = []
            
            # Yield remaining items
            for item in batch:
                yield item
    
    async def _stream_api_data(self, source_config: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Stream data from government API"""
        
        api_url = source_config.get("api_url", "")
        api_key = source_config.get("api_key", "")
        batch_size = source_config.get("batch_size", 100)
        
        # Implementation would handle pagination and API rate limits
        # This is a mock implementation
        
        offset = 0
        while True:
            # Simulate API call
            api_records = await self._fetch_api_batch(api_url, api_key, offset, batch_size)
            
            if not api_records:
                break
            
            for record in api_records:
                msme_record = self._transform_api_record(record)
                yield msme_record
            
            offset += batch_size
            
            # Rate limiting
            await asyncio.sleep(0.1)
    
    def _transform_csv_record(self, record: Dict[str, str]) -> Dict[str, Any]:
        """Transform CSV record to standard MSME format"""
        
        try:
            # Parse financial values
            investment = float(record.get('investment_in_plant', '0').replace(',', ''))
            turnover = float(record.get('annual_turnover', '0').replace(',', ''))
            employees = int(record.get('total_employees', '0'))
            
            # Parse registration date
            reg_date_str = record.get('registration_date', '')
            if reg_date_str:
                reg_date = datetime.strptime(reg_date_str, '%Y-%m-%d').isoformat() + 'Z'
            else:
                reg_date = datetime.now().isoformat() + 'Z'
            
            # Build standard MSME record structure
            msme_record = {
                "udyam_number": record.get('udyam_number', ''),
                "registration_date": reg_date,
                "enterprise_details": {
                    "enterprise_name": record.get('enterprise_name', ''),
                    "constitution": record.get('constitution', 'Proprietorship'),
                    "activity_type": self._map_activity_type(record.get('nic_code', '')),
                    "nic_code": record.get('nic_code', ''),
                    "nic_description": record.get('nic_description', ''),
                    "district": record.get('district', ''),
                    "state": record.get('state', '')
                },
                "classification": {
                    "category": record.get('category', 'Micro'),
                    "investment_in_plant": investment,
                    "annual_turnover": turnover,
                    "classification_criteria": self._get_classification_criteria(record.get('category', 'Micro'))
                },
                "identification": {
                    "pan": record.get('pan', ''),
                    "gstin": record.get('gstin', ''),
                    "aadhaar_linked": record.get('aadhaar_linked', '').lower() in ['true', '1', 'yes']
                },
                "employment": {
                    "total_employees": employees,
                    "male_employees": int(record.get('male_employees', str(int(employees * 0.6)))),
                    "female_employees": int(record.get('female_employees', str(int(employees * 0.4))))
                },
                "financial_year": record.get('financial_year', '2024-25'),
                "status": record.get('status', 'Active')
            }
            
            return msme_record
            
        except Exception as e:
            raise ValueError(f"Failed to transform CSV record: {e}")
    
    def _transform_api_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform API record to standard MSME format"""
        # Similar transformation logic for API data
        # Implementation would depend on the specific API response format
        return record
    
    def _map_activity_type(self, nic_code: str) -> str:
        """Map NIC code to activity type"""
        if not nic_code:
            return "Service"
        
        nic_first_two = nic_code[:2]
        
        # Manufacturing (NIC codes 10-33)
        if '10' <= nic_first_two <= '33':
            return "Manufacturing"
        
        # Trading/Wholesale/Retail (NIC codes 45-47)
        elif '45' <= nic_first_two <= '47':
            return "Trading"
        
        # Services (everything else)
        else:
            return "Service"
    
    def _get_classification_criteria(self, category: str) -> Dict[str, float]:
        """Get classification criteria for MSME category"""
        
        criteria_map = {
            "Micro": {
                "investment_limit": 2500000.0,   # 25 lakh
                "turnover_limit": 10000000.0     # 1 crore
            },
            "Small": {
                "investment_limit": 25000000.0,  # 25 crore
                "turnover_limit": 100000000.0    # 100 crore
            },
            "Medium": {
                "investment_limit": 125000000.0, # 125 crore
                "turnover_limit": 500000000.0    # 500 crore
            }
        }
        
        return criteria_map.get(category, criteria_map["Micro"])
    
    async def _fetch_api_batch(self, api_url: str, api_key: str, offset: int, limit: int) -> List[Dict[str, Any]]:
        """Mock API fetch - in real implementation, this would call the actual API"""
        
        # Mock implementation - returns empty list to end streaming
        return []
    
    def transform_for_learning(self, msme_record: Dict[str, Any]) -> str:
        """Transform MSME record into content suitable for Sutra's learning pipeline"""
        
        details = msme_record['enterprise_details']
        classification = msme_record['classification']
        employment = msme_record['employment']
        
        # Build comprehensive content for semantic understanding
        learning_content = f"""MSME Enterprise Registration: {details['enterprise_name']}

Registration Information:
- Udyam Number: {msme_record['udyam_number']}
- Registration Date: {msme_record['registration_date']}
- Status: {msme_record['status']}

Business Profile:
- Legal Constitution: {details['constitution']}
- Business Activity: {details['activity_type']}
- Industry: {details['nic_description']} (NIC: {details['nic_code']})
- Business Location: {details['district']}, {details['state']}, India

MSME Classification:
- Category: {classification['category']} Enterprise
- Investment in Plant & Machinery: Rs. {classification['investment_in_plant']:,.2f}
- Annual Turnover: Rs. {classification['annual_turnover']:,.2f}

Employment Profile:
- Total Employees: {employment['total_employees']}
- Male Employees: {employment['male_employees']}
- Female Employees: {employment['female_employees']}
- Employment Intensity: {employment['total_employees'] / max(1, classification['investment_in_plant'] / 1000000):.2f} employees per million invested

Compliance Status:
- PAN: {msme_record['identification']['pan']}
- GSTIN: {msme_record['identification']['gstin']}
- Aadhaar Linked: {'Yes' if msme_record['identification']['aadhaar_linked'] else 'No'}

Economic Context:
- Financial Year: {msme_record['financial_year']}
- Economic Sector: {self._get_economic_sector(details['activity_type'])}
- Regional Context: {self._get_regional_context(details['state'])}
"""
        
        return learning_content
    
    def _get_economic_sector(self, activity_type: str) -> str:
        """Map activity type to economic sector"""
        sector_map = {
            "Manufacturing": "Secondary Sector (Industrial Production)",
            "Trading": "Tertiary Sector (Commercial Distribution)",
            "Service": "Tertiary Sector (Service Delivery)"
        }
        return sector_map.get(activity_type, "Mixed Economic Activity")
    
    def _get_regional_context(self, state: str) -> str:
        """Get regional economic context"""
        region_map = {
            "Maharashtra": "Western India Industrial and Financial Hub",
            "Karnataka": "Southern India Technology and Innovation Center",
            "Tamil Nadu": "Southern India Manufacturing and Automotive Hub",
            "Gujarat": "Western India Business and Trade Center",
            "Delhi": "National Capital Region Administrative Center",
            "West Bengal": "Eastern India Commercial and Cultural Hub",
            "Uttar Pradesh": "Northern India Population and Agricultural Center",
            "Rajasthan": "Northwestern India Tourism and Mining Region",
            "Haryana": "Northern India Industrial and Agricultural Belt",
            "Punjab": "Northern India Agricultural Powerhouse",
            "Andhra Pradesh": "Southern India Emerging Industrial Hub",
            "Telangana": "Southern India Information Technology Hub"
        }
        return region_map.get(state, "Regional Economic Development Center")

# Plugin registration function required by Sutra bulk ingester
def create_adapter(config: Dict[str, Any]) -> MSMEAdapter:
    """Factory function to create MSME adapter instance"""
    return MSMEAdapter(config)

# Plugin metadata
PLUGIN_INFO = {
    "name": "msme_csv_adapter",
    "version": "1.0.0",
    "description": "Government of India MSME data adapter for Sutra bulk ingestion",
    "author": "Sutra AI Team",
    "supported_formats": ["csv", "json", "api"],
    "required_config": [
        "source_type",  # csv, json, or api
        "csv_path",     # for CSV sources
        "api_url",      # for API sources
        "encoding"      # text encoding (default: utf-8)
    ]
}

if __name__ == "__main__":
    # Test the adapter with sample data
    import asyncio
    
    async def test_adapter():
        config = {
            "batch_size": 100,
            "memory_limit_mb": 512
        }
        
        adapter = MSMEAdapter(config)
        
        # Test CSV validation
        source_config = {
            "source_type": "csv",
            "csv_path": "sample_msme_data.csv",
            "encoding": "utf-8",
            "chunk_size": 50
        }
        
        try:
            print("Testing adapter validation...")
            is_valid = await adapter.validate_source(source_config)
            print(f"Validation result: {is_valid}")
            
            print("Estimating total items...")
            total_items = await adapter.estimate_total_items(source_config)
            print(f"Estimated items: {total_items}")
            
        except Exception as e:
            print(f"Test failed: {e}")
    
    # Note: This test would fail without actual CSV file
    # asyncio.run(test_adapter())