#!/usr/bin/env python3
"""
Debug Financial Ingestion - Simple test to identify issues
"""

import requests
import json
from typing import Dict, Any
from datetime import datetime, timedelta

class DebugFinancialIngestor:
    def __init__(self):
        self.base_url = "http://localhost:8080/api"
        self.session = requests.Session()
    
    def create_concept(self, ticker: str, date: datetime) -> Dict[str, Any]:
        """Create a realistic financial concept"""
        # Generate realistic market data
        import random
        base_price = {"AAPL": 180, "MSFT": 380, "GOOGL": 140}[ticker]
        price_change = random.uniform(-0.05, 0.05)
        close_price = round(base_price * (1 + price_change), 2)
        open_price = round(close_price * random.uniform(0.98, 1.02), 2)
        high_price = round(max(open_price, close_price) * random.uniform(1.0, 1.03), 2)
        low_price = round(min(open_price, close_price) * random.uniform(0.97, 1.0), 2)
        volume = random.randint(50000000, 150000000)
        
        return {
            "content": f"{ticker} stock traded on {date.strftime('%Y-%m-%d')} with closing price ${close_price:.2f}. "
                      f"The stock opened at ${open_price:.2f}, reached a high of ${high_price:.2f}, "
                      f"and a low of ${low_price:.2f}. Trading volume was {volume:,} shares. "
                      f"Daily change: {((close_price - open_price) / open_price * 100):+.2f}%",
            "metadata": {
                "source": "financial_market_data",
                "company": ticker,
                "date": date.strftime('%Y-%m-%d'),
                "data_type": "daily_ohlcv",
                "price_open": str(open_price),
                "price_close": str(close_price),
                "price_high": str(high_price),
                "price_low": str(low_price),
                "volume": str(volume),
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def test_single_concept(self, ticker: str = "AAPL"):
        """Test creating a single concept"""
        print(f"🧪 Testing single concept creation for {ticker}")
        
        concept = self.create_concept(ticker, datetime.now() - timedelta(days=1))
        
        print(f"📝 Concept content preview: {concept['content'][:100]}...")
        print(f"📊 Metadata keys: {list(concept['metadata'].keys())}")
        
        try:
            response = self.session.post(f"{self.base_url}/learn", json=concept, timeout=30)
            print(f"📡 Response status: {response.status_code}")
            print(f"📡 Response headers: {dict(response.headers)}")
            print(f"📡 Response text: {response.text}")
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Success! Concept ID: {result.get('concept_id')}")
                return True
            else:
                print(f"❌ Failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"💥 Exception occurred: {e}")
            return False
    
    def test_api_health(self):
        """Test API health endpoint"""
        print("🏥 Testing API health...")
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            print(f"📡 Health status: {response.status_code}")
            print(f"📡 Health response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"💥 Health check failed: {e}")
            return False
    
    def test_multiple_concepts(self, count: int = 3):
        """Test creating multiple concepts"""
        print(f"🧪 Testing {count} concept creations")
        
        success_count = 0
        companies = ["AAPL", "MSFT", "GOOGL"]
        
        for i in range(count):
            ticker = companies[i % len(companies)]
            date = datetime.now() - timedelta(days=i+1)
            
            concept = self.create_concept(ticker, date)
            
            try:
                response = self.session.post(f"{self.base_url}/learn", json=concept, timeout=30)
                
                if response.status_code == 201:
                    result = response.json()
                    concept_id = result.get('concept_id', 'unknown')
                    print(f"✅ {ticker} concept created: {concept_id}")
                    success_count += 1
                else:
                    print(f"❌ {ticker} failed: {response.status_code} - {response.text[:100]}")
                    
            except Exception as e:
                print(f"💥 {ticker} exception: {e}")
        
        print(f"📊 Success rate: {success_count}/{count} ({100*success_count/count:.1f}%)")
        return success_count == count

def main():
    print("🐛 DEBUG FINANCIAL INGESTION")
    print("=" * 50)
    
    debug = DebugFinancialIngestor()
    
    # Test 1: API Health
    print("\n1️⃣ API Health Check")
    health_ok = debug.test_api_health()
    
    if not health_ok:
        print("❌ API health check failed. Stopping tests.")
        return
    
    # Test 2: Single concept
    print("\n2️⃣ Single Concept Test")
    single_ok = debug.test_single_concept()
    
    # Test 3: Multiple concepts
    print("\n3️⃣ Multiple Concepts Test")
    multiple_ok = debug.test_multiple_concepts(5)
    
    # Summary
    print("\n📊 DEBUG SUMMARY")
    print("=" * 50)
    print(f"Health Check: {'✅' if health_ok else '❌'}")
    print(f"Single Concept: {'✅' if single_ok else '❌'}")
    print(f"Multiple Concepts: {'✅' if multiple_ok else '❌'}")
    
    if all([health_ok, single_ok, multiple_ok]):
        print("\n🎉 All tests passed! Production script should work.")
    else:
        print("\n🚨 Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()