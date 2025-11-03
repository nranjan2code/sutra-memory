#!/usr/bin/env python3
"""
MSME Continuous Learning Pipeline
Government of India MSME data integration with Sutra AI platform

This script demonstrates real-world continuous learning from government data
following Sutra's unified architecture - no shortcuts, proper pipeline usage.
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from faker import Faker
import aiohttp
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SutraClient:
    """Sutra AI client for learning concepts and querying knowledge"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def learn_concept(self, content: str, options: Dict[str, Any] = None) -> str:
        """Learn a concept through Sutra's unified learning pipeline"""
        if not options:
            options = {
                "generate_embedding": True,
                "extract_associations": True,
                "analyze_semantics": True,
                "strength": 1.0,
                "confidence": 0.95
            }
        
        payload = {
            "content": content,
            "options": options
        }
        
        async with self.session.post(f"{self.base_url}/learn", json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("concept_id")
            else:
                error_text = await response.text()
                raise Exception(f"Failed to learn concept: {response.status} - {error_text}")
    
    async def learn_association(self, source: str, target: str, 
                              association_type: str, confidence: float) -> bool:
        """Create association between concepts"""
        payload = {
            "source": source,
            "target": target,
            "association_type": association_type,
            "confidence": confidence
        }
        
        async with self.session.post(f"{self.base_url}/associate", json=payload) as response:
            return response.status == 200
    
    async def query(self, query_text: str) -> Dict[str, Any]:
        """Query the knowledge graph"""
        payload = {"query": query_text}
        
        async with self.session.post(f"{self.base_url}/query", json=payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"Query failed: {response.status} - {error_text}")

class MSMEDataGenerator:
    """Generate realistic synthetic MSME data for testing continuous learning"""
    
    def __init__(self):
        self.fake = Faker('en_IN')  # Indian locale
        
        # Indian states and major districts for realistic data
        self.indian_locations = [
            ("Maharashtra", "Mumbai"), ("Maharashtra", "Pune"), ("Maharashtra", "Nashik"),
            ("Karnataka", "Bangalore Urban"), ("Karnataka", "Mysore"), ("Karnataka", "Hubli"),
            ("Tamil Nadu", "Chennai"), ("Tamil Nadu", "Coimbatore"), ("Tamil Nadu", "Madurai"),
            ("Gujarat", "Ahmedabad"), ("Gujarat", "Surat"), ("Gujarat", "Vadodara"),
            ("Delhi", "New Delhi"), ("Delhi", "South Delhi"), ("Delhi", "East Delhi"),
            ("West Bengal", "Kolkata"), ("West Bengal", "Howrah"), ("West Bengal", "Durgapur"),
            ("Rajasthan", "Jaipur"), ("Rajasthan", "Jodhpur"), ("Rajasthan", "Udaipur"),
            ("Uttar Pradesh", "Lucknow"), ("Uttar Pradesh", "Kanpur"), ("Uttar Pradesh", "Agra"),
            ("Haryana", "Gurugram"), ("Haryana", "Faridabad"),
            ("Punjab", "Ludhiana"), ("Punjab", "Amritsar"),
            ("Andhra Pradesh", "Visakhapatnam"), ("Andhra Pradesh", "Vijayawada"),
            ("Telangana", "Hyderabad"), ("Telangana", "Warangal"),
        ]
        
        # Common MSME industries with realistic NIC codes
        self.industries = [
            ("25920", "Manufacture of plastic packing goods", "Manufacturing"),
            ("46900", "Non-specialised wholesale trade", "Trading"),
            ("62090", "Other information technology service activities", "Service"),
            ("70200", "Management consultancy activities", "Service"),
            ("15111", "Processing and preserving of meat", "Manufacturing"),
            ("13201", "Weaving of cotton textiles", "Manufacturing"),
            ("23091", "Manufacture of ready-mix concrete", "Manufacturing"),
            ("46491", "Wholesale of pharmaceutical goods", "Trading"),
            ("56101", "Restaurants and mobile food service activities", "Service"),
            ("95110", "Repair of computers and peripheral equipment", "Service"),
            ("13911", "Manufacture of knitted and crocheted fabrics", "Manufacturing"),
            ("20291", "Manufacture of other chemical products", "Manufacturing"),
            ("47521", "Retail sale of textiles", "Trading"),
            ("68201", "Renting and operating of own or leased real estate", "Service"),
            ("74999", "Other professional, scientific and technical activities", "Service"),
        ]
        
        self.constitutions = [
            "Proprietorship", "Partnership", "Private Limited Company", 
            "Public Limited Company", "LLP", "Hindu Undivided Family"
        ]
    
    def generate_single_msme(self, sequential_id: int) -> Dict[str, Any]:
        """Generate a single realistic MSME record"""
        
        state, district = random.choice(self.indian_locations)
        nic_code, nic_desc, activity = random.choice(self.industries)
        
        # Realistic category distribution (85% Micro, 12% Small, 3% Medium)
        category = random.choices(
            ["Micro", "Small", "Medium"], 
            weights=[85, 12, 3]
        )[0]
        
        # Generate realistic financials based on category
        if category == "Micro":
            investment = random.uniform(50000, 2500000)    # 50K to 25L
            turnover = random.uniform(100000, 10000000)    # 1L to 1Cr
        elif category == "Small":
            investment = random.uniform(2500000, 25000000)  # 25L to 25Cr
            turnover = random.uniform(10000000, 100000000)  # 1Cr to 100Cr
        else:  # Medium
            investment = random.uniform(25000000, 125000000)  # 25Cr to 125Cr
            turnover = random.uniform(100000000, 500000000)  # 100Cr to 500Cr
        
        # Employment realistic for category
        if category == "Micro":
            employees = random.randint(1, 10)
        elif category == "Small":
            employees = random.randint(11, 50)
        else:
            employees = random.randint(51, 250)
        
        # Gender distribution with realistic bias
        male_ratio = random.uniform(0.55, 0.75)  # Slight male bias in Indian MSMEs
        male_employees = int(employees * male_ratio)
        female_employees = employees - male_employees
        
        # Registration date in realistic range (last 5 years)
        reg_date = self.fake.date_time_between(
            start_date=datetime(2020, 7, 1), 
            end_date=datetime.now()
        )
        
        # Generate realistic company name
        business_types = ['Industries', 'Traders', 'Services', 'Enterprises', 'Corporation', 
                         'Solutions', 'Systems', 'Manufacturing', 'Trading Co', 'Pvt Ltd']
        company_name = f"{self.fake.company()} {random.choice(business_types)}"
        
        return {
            "udyam_number": f"UDYAM-{state[:2].upper()}-{reg_date.year % 100:02d}-{sequential_id:07d}",
            "registration_date": reg_date.isoformat() + "Z",
            "enterprise_details": {
                "enterprise_name": company_name,
                "constitution": random.choice(self.constitutions),
                "activity_type": activity,
                "nic_code": nic_code,
                "nic_description": nic_desc,
                "district": district,
                "state": state
            },
            "classification": {
                "category": category,
                "investment_in_plant": round(investment, 2),
                "annual_turnover": round(turnover, 2),
                "classification_criteria": {
                    "investment_limit": 2500000 if category == "Micro" else (25000000 if category == "Small" else 125000000),
                    "turnover_limit": 10000000 if category == "Micro" else (100000000 if category == "Small" else 500000000)
                }
            },
            "identification": {
                "pan": self.fake.random_element(["ABCDE1234F", "PQRST5678G", "LMNOP9012H", "XYZAB5678C"]),
                "gstin": f"{random.randint(10,35)}{self.fake.random_element(['ABCDE1234F', 'PQRST5678G'])}1Z{random.randint(1,9)}",
                "aadhaar_linked": random.choices([True, False], weights=[90, 10])[0]
            },
            "employment": {
                "total_employees": employees,
                "male_employees": male_employees,
                "female_employees": female_employees
            },
            "financial_year": f"{reg_date.year}-{(reg_date.year + 1) % 100:02d}",
            "status": random.choices(["Active", "Inactive", "Suspended"], weights=[92, 6, 2])[0]
        }
    
    def generate_batch(self, count: int, start_id: int = 1) -> List[Dict[str, Any]]:
        """Generate a batch of MSME records"""
        return [self.generate_single_msme(start_id + i) for i in range(count)]

class MSMELearningPipeline:
    """Pipeline for learning MSME data through Sutra's unified architecture"""
    
    def __init__(self, sutra_client: SutraClient):
        self.client = sutra_client
        self.learned_concepts = {}  # Cache for learned concept IDs
    
    async def learn_msme_enterprise(self, msme_data: Dict[str, Any]) -> str:
        """Learn a single MSME enterprise following Sutra's pipeline"""
        
        # 1. Primary enterprise concept - comprehensive semantic content
        enterprise_content = self._build_enterprise_content(msme_data)
        
        enterprise_id = await self.client.learn_concept(
            content=enterprise_content,
            options={
                "generate_embedding": True,
                "extract_associations": True,
                "analyze_semantics": True,  # Enable 9-type semantic classification
                "strength": 1.0,
                "confidence": 0.95
            }
        )
        
        # 2. Learn and associate industry classification
        await self._learn_industry_association(enterprise_id, msme_data)
        
        # 3. Learn and associate geographical context
        await self._learn_location_association(enterprise_id, msme_data)
        
        # 4. Learn and associate temporal registration event
        await self._learn_registration_event(enterprise_id, msme_data)
        
        # 5. Learn and associate employment patterns
        await self._learn_employment_data(enterprise_id, msme_data)
        
        return enterprise_id
    
    def _build_enterprise_content(self, msme_data: Dict[str, Any]) -> str:
        """Build comprehensive enterprise content for semantic understanding"""
        details = msme_data['enterprise_details']
        classification = msme_data['classification']
        employment = msme_data['employment']
        
        content = f"""Enterprise Profile: {details['enterprise_name']}

Business Information:
- Legal Constitution: {details['constitution']}
- Business Activity: {details['activity_type']}
- Industry Sector: {details['nic_description']} (NIC Code: {details['nic_code']})
- Business Location: {details['district']}, {details['state']}, India

MSME Classification:
- Category: {classification['category']} Enterprise
- Investment in Plant & Machinery: Rs. {classification['investment_in_plant']:,.2f}
- Annual Turnover: Rs. {classification['annual_turnover']:,.2f}
- Classification Criteria: Investment ≤ Rs. {classification['classification_criteria']['investment_limit']:,}, Turnover ≤ Rs. {classification['classification_criteria']['turnover_limit']:,}

Employment Profile:
- Total Workforce: {employment['total_employees']} employees
- Gender Distribution: {employment['male_employees']} male, {employment['female_employees']} female employees
- Employment Density: {self._get_employment_category(employment['total_employees'])}

Registration Details:
- Udyam Registration Number: {msme_data['udyam_number']}
- Registration Date: {msme_data['registration_date']}
- Financial Year: {msme_data['financial_year']}
- Current Status: {msme_data['status']}

Government Compliance:
- PAN: {msme_data['identification']['pan']}
- GSTIN: {msme_data['identification']['gstin']}
- Aadhaar Linked: {'Yes' if msme_data['identification']['aadhaar_linked'] else 'No'}
"""
        return content
    
    async def _learn_industry_association(self, enterprise_id: str, msme_data: Dict[str, Any]):
        """Learn industry classification and create associations"""
        details = msme_data['enterprise_details']
        
        industry_key = f"industry_{details['nic_code']}"
        if industry_key not in self.learned_concepts:
            industry_content = f"""Industry Classification: {details['nic_description']}
NIC Code: {details['nic_code']}
Activity Type: {details['activity_type']}
Economic Sector: {self._get_economic_sector(details['activity_type'])}
"""
            
            industry_id = await self.client.learn_concept(
                content=industry_content,
                options={"extract_associations": True, "analyze_semantics": True}
            )
            self.learned_concepts[industry_key] = industry_id
        
        # Create industry association
        await self.client.learn_association(
            source=enterprise_id,
            target=self.learned_concepts[industry_key],
            association_type="categorical",
            confidence=0.95
        )
    
    async def _learn_location_association(self, enterprise_id: str, msme_data: Dict[str, Any]):
        """Learn geographical context and associations"""
        details = msme_data['enterprise_details']
        
        location_key = f"location_{details['state']}_{details['district']}"
        if location_key not in self.learned_concepts:
            location_content = f"""Business Location: {details['district']} District
State: {details['state']}
Country: India
Regional Context: {self._get_regional_context(details['state'])}
Economic Zone: {self._get_economic_zone(details['state'], details['district'])}
"""
            
            location_id = await self.client.learn_concept(
                content=location_content,
                options={"analyze_semantics": True}
            )
            self.learned_concepts[location_key] = location_id
        
        # Create spatial association
        await self.client.learn_association(
            source=enterprise_id,
            target=self.learned_concepts[location_key],
            association_type="spatial",
            confidence=0.9
        )
    
    async def _learn_registration_event(self, enterprise_id: str, msme_data: Dict[str, Any]):
        """Learn registration as temporal event"""
        reg_date = datetime.fromisoformat(msme_data['registration_date'].replace('Z', '+00:00'))
        
        event_content = f"""MSME Registration Event: {msme_data['udyam_number']}
Event Type: Business Registration
Registration Date: {reg_date.strftime('%B %d, %Y')}
Financial Year: {msme_data['financial_year']}
Enterprise: {msme_data['enterprise_details']['enterprise_name']}
Initial Classification: {msme_data['classification']['category']} Enterprise
Government System: Udyam Registration Portal
Legal Framework: MSME Development Act, 2006
"""
        
        event_id = await self.client.learn_concept(
            content=event_content,
            options={"analyze_semantics": True}  # Will classify as Event type
        )
        
        # Create temporal association
        await self.client.learn_association(
            source=event_id,
            target=enterprise_id,
            association_type="temporal",
            confidence=0.95
        )
    
    async def _learn_employment_data(self, enterprise_id: str, msme_data: Dict[str, Any]):
        """Learn employment patterns and relationships"""
        employment = msme_data['employment']
        
        if employment['total_employees'] > 0:
            employment_content = f"""Employment Statistics: {msme_data['enterprise_details']['enterprise_name']}
Total Workforce: {employment['total_employees']} employees
Gender Distribution: {employment['male_employees']} male ({employment['male_employees']/employment['total_employees']*100:.1f}%), {employment['female_employees']} female ({employment['female_employees']/employment['total_employees']*100:.1f}%)
Employment Category: {self._get_employment_category(employment['total_employees'])}
Employment Density: {employment['total_employees']/max(1, msme_data['classification']['investment_in_plant']/1000000):.2f} employees per million invested
Workforce Scale: {self._get_workforce_scale(employment['total_employees'])}
"""
            
            employment_id = await self.client.learn_concept(
                content=employment_content,
                options={"analyze_semantics": True}
            )
            
            # Create quantitative association
            await self.client.learn_association(
                source=enterprise_id,
                target=employment_id,
                association_type="quantitative",
                confidence=0.9
            )
    
    # Helper methods for categorization
    def _get_employment_category(self, count: int) -> str:
        if count <= 10:
            return "Micro Employment Scale"
        elif count <= 50:
            return "Small Employment Scale"
        elif count <= 250:
            return "Medium Employment Scale"
        else:
            return "Large Employment Scale"
    
    def _get_workforce_scale(self, count: int) -> str:
        if count <= 5:
            return "Minimal Workforce"
        elif count <= 20:
            return "Compact Team"
        elif count <= 100:
            return "Medium Team"
        else:
            return "Large Team"
    
    def _get_economic_sector(self, activity_type: str) -> str:
        sector_map = {
            "Manufacturing": "Secondary Sector (Industrial)",
            "Trading": "Tertiary Sector (Commercial)",
            "Service": "Tertiary Sector (Services)"
        }
        return sector_map.get(activity_type, "Mixed Sector")
    
    def _get_regional_context(self, state: str) -> str:
        region_map = {
            "Maharashtra": "Western India Industrial Hub",
            "Karnataka": "Southern India Technology Hub", 
            "Tamil Nadu": "Southern India Manufacturing Hub",
            "Gujarat": "Western India Business Hub",
            "Delhi": "National Capital Region",
            "West Bengal": "Eastern India Commercial Hub",
            "Uttar Pradesh": "Northern India Population Center",
            "Rajasthan": "Northwestern India Tourism & Mining Hub",
            "Haryana": "Northern India Industrial Belt",
            "Punjab": "Northern India Agricultural Hub",
            "Andhra Pradesh": "Southern India Emerging Hub",
            "Telangana": "Southern India IT Hub"
        }
        return region_map.get(state, "Regional Economic Center")
    
    def _get_economic_zone(self, state: str, district: str) -> str:
        # Simplified economic zone mapping
        if district in ["Mumbai", "Pune", "Ahmedabad", "Surat"]:
            return "Tier-1 Economic Zone"
        elif district in ["Bangalore Urban", "Chennai", "Hyderabad", "Kolkata"]:
            return "Tier-1 Technology Zone"
        elif district in ["Gurugram", "Faridabad", "New Delhi"]:
            return "NCR Economic Zone"
        else:
            return "Tier-2 Economic Zone"

async def main():
    """Main execution function demonstrating MSME continuous learning"""
    
    logger.info("🚀 Starting MSME Continuous Learning Pipeline")
    logger.info("Following Sutra's unified architecture - no shortcuts!")
    
    # Initialize components
    async with SutraClient("http://localhost:8000") as sutra_client:
        msme_generator = MSMEDataGenerator()
        learning_pipeline = MSMELearningPipeline(sutra_client)
        
        # Test with smaller batch first
        batch_size = 100
        logger.info(f"📊 Generating {batch_size} synthetic MSME records...")
        
        msme_batch = msme_generator.generate_batch(batch_size)
        
        # Continuous learning simulation
        logger.info("🧠 Starting continuous learning process...")
        start_time = datetime.now()
        
        learned_count = 0
        failed_count = 0
        
        for i, msme_data in enumerate(msme_batch):
            try:
                enterprise_id = await learning_pipeline.learn_msme_enterprise(msme_data)
                learned_count += 1
                
                if (i + 1) % 20 == 0:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    rate = (i + 1) / elapsed
                    logger.info(f"✅ Progress: {i+1}/{batch_size} | Rate: {rate:.1f} MSMEs/sec | Success: {learned_count} | Failed: {failed_count}")
                
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ Failed to learn MSME {msme_data.get('udyam_number', 'unknown')}: {e}")
            
            # Maintain reasonable rate (respecting <10ms promise + network overhead)
            await asyncio.sleep(0.01)  # 10ms delay
        
        total_time = (datetime.now() - start_time).total_seconds()
        final_rate = batch_size / total_time
        
        logger.info(f"🎉 Learning Complete!")
        logger.info(f"📊 Results: {learned_count} learned, {failed_count} failed")
        logger.info(f"⚡ Performance: {total_time:.1f}s total, {final_rate:.1f} MSMEs/sec")
        logger.info(f"🔍 Average per concept: {(total_time/batch_size)*1000:.1f}ms (target: <10ms)")
        
        # Demonstrate learned knowledge with queries
        logger.info("\n🧠 Testing Learned Knowledge...")
        
        test_queries = [
            "Show me MSME registrations in Maharashtra",
            "What industries have the highest employment in Karnataka?",
            "How many Micro enterprises were registered in 2024?",
            "Which states have the most Manufacturing MSMEs?",
            "Show the relationship between investment and employment"
        ]
        
        for query in test_queries:
            try:
                logger.info(f"🔍 Query: {query}")
                result = await sutra_client.query(query)
                logger.info(f"✅ Response: {result.get('summary', 'No summary')}")
            except Exception as e:
                logger.error(f"❌ Query failed: {e}")
            
            await asyncio.sleep(1)  # Brief pause between queries

if __name__ == "__main__":
    asyncio.run(main())