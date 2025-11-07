# Google Finance Data Integration Guide

## Complete End-to-End Process

This guide shows you exactly how to ingest Google Finance data and make it available for querying in the Sutra platform.

## Prerequisites

1. **Sutra Platform Running**
   ```bash
   SUTRA_EDITION=simple sutra deploy
   sutra status  # Verify all services are running
   ```

2. **Google API Setup**
   - Google Cloud Project with Sheets API enabled
   - API key from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Google Sheet with GOOGLEFINANCE formulas

3. **Access Points**
   - Web UI: http://localhost:3000
   - API: http://localhost:8000
   - Storage: localhost:7000

## Step-by-Step Integration Process

### Step 1: Create Google Sheet with Financial Data

#### Option A: Use Our Template (Recommended)
1. Copy this template: [Financial Data Template](https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms)
2. Make it publicly readable (Share > Anyone with link can view)
3. Note the sheet ID from the URL

#### Option B: Create Your Own Sheet
Create a new Google Sheet with this structure:

| A (Date) | B (Ticker) | C (Price) | D (Volume) | E (Market Cap) | F (P/E) | G (Div Yield) | H (Beta) |
|----------|------------|-----------|------------|----------------|---------|---------------|----------|
| Date | Ticker | Price | Volume | Market Cap | P/E Ratio | Dividend Yield | Beta |
| 2025-11-07 | NVDA | `=GOOGLEFINANCE("NVDA","price")` | `=GOOGLEFINANCE("NVDA","volume")` | `=GOOGLEFINANCE("NVDA","marketcap")` | `=GOOGLEFINANCE("NVDA","pe")` | `=GOOGLEFINANCE("NVDA","dividendyield")` | `=GOOGLEFINANCE("NVDA","beta")` |
| 2025-11-07 | GOOGL | `=GOOGLEFINANCE("GOOGL","price")` | `=GOOGLEFINANCE("GOOGL","volume")` | `=GOOGLEFINANCE("GOOGL","marketcap")` | `=GOOGLEFINANCE("GOOGL","pe")` | `=GOOGLEFINANCE("GOOGL","dividendyield")` | `=GOOGLEFINANCE("GOOGL","beta")` |

Add rows for: MSFT, TSLA, AAPL, AMZN, META, NFLX, CRM, NVDA, AMD, etc.

### Step 2: Configure Ingestion

Create your configuration file:

```bash
cp examples/financial_data/basic_config.json my_financial_config.json
```

Edit `my_financial_config.json`:
```json
{
  "spreadsheet_id": "YOUR_ACTUAL_SHEET_ID_HERE",
  "sheet_name": "FinancialData",
  "range": "A1:H1000", 
  "api_key": "YOUR_GOOGLE_API_KEY_HERE",
  "sutra_api_url": "http://localhost:8000",
  "sutra_storage_url": "localhost:7000",
  "batch_size": 100,
  "target_companies": [
    "NVDA", "GOOGL", "MSFT", "TSLA", "AAPL", "AMZN", "META"
  ],
  "enable_temporal_reasoning": true,
  "enable_causal_analysis": true
}
```

### Step 3: Run Data Ingestion

#### Quick Setup (Automated)
```bash
# Run the automated setup script
./scripts/setup-google-finance.sh
```

#### Manual Ingestion
```bash
# Test configuration first (dry run)
python examples/financial_ingester.py \
  --config my_financial_config.json \
  --dry-run

# Run actual ingestion
python examples/financial_ingester.py \
  --config my_financial_config.json
```

#### Command Line Options
```bash
# Specific companies
python examples/financial_ingester.py \
  --sheet-id "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms" \
  --api-key "AIza..." \
  --companies "NVDA,GOOGL,MSFT,TSLA"

# Date range filtering
python examples/financial_ingester.py \
  --config my_financial_config.json \
  --start-date "2024-01-01" \
  --end-date "2025-11-07"
```

### Step 4: Verify Data Ingestion

Check that data was ingested successfully:

```bash
# Check Sutra status
sutra status

# Validate learning capabilities
python examples/financial_data/test_financial_learning.py --quick-test

# Check storage stats via API
curl http://localhost:8000/api/v1/stats
```

Expected output:
```json
{
  "status": "success",
  "concepts_ingested": 150,
  "companies_processed": 7,
  "processing_time_seconds": 12.3,
  "concepts_per_second": 12.2
}
```

### Step 5: Query Financial Data

Now you can query the financial data through multiple interfaces:

#### Web UI (Recommended)
1. Open http://localhost:3000
2. Try these queries:
   - "What is NVDA's current stock price?"
   - "Compare trading volumes of tech companies"
   - "Show me companies with high P/E ratios"
   - "What caused tech stock volatility?"

#### API Queries
```bash
# Basic financial query
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is NVDA stock price and volume?"}'

# Temporal reasoning query  
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Which companies had high trading volume this week?"}'

# Causal analysis query
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What factors influence NVDA price movements?"}'
```

#### Python API Client
```python
import asyncio
from sutra_client.client import SutraClient

async def query_financial_data():
    client = SutraClient(api_url="http://localhost:8000")
    
    # Basic query
    result = await client.query("What is NVDA's market cap?")
    print("Basic Query:", result)
    
    # Complex analysis
    result = await client.query(
        "Compare the P/E ratios of AI companies like NVDA, AMD, and GOOGL"
    )
    print("Analysis:", result)
    
    # Temporal reasoning
    result = await client.query(
        "Show me trading volume patterns for tech stocks over time"
    )
    print("Temporal:", result)

asyncio.run(query_financial_data())
```

## Advanced Features

### Historical Data Ingestion

For bulk historical data, create a sheet with this formula in A1:
```
=GOOGLEFINANCE("NVDA","all",DATE(2024,1,1),DATE(2025,11,7),"DAILY")
```

Then ingest with historical configuration:
```bash
python examples/financial_ingester.py \
  --config examples/financial_data/historical_config.json
```

### Real-Time Updates

Set up periodic ingestion with cron:
```bash
# Add to crontab (run every hour during market hours)
0 9-16 * * 1-5 cd /path/to/sutra && python examples/financial_ingester.py --config my_financial_config.json
```

### Bulk Processing Multiple Sheets

For multiple data sources:
```bash
# Process multiple companies/sheets
for config in configs/nvda_data.json configs/googl_data.json; do
    python examples/financial_ingester.py --config $config
done
```

## Example Queries You Can Now Ask

Once data is ingested, Sutra understands these types of financial questions:

### **Stock Analysis**
- "What is NVDA's current stock price and trading volume?"
- "Show me the market cap of all AI companies"  
- "Which tech stocks have the highest P/E ratios?"
- "Compare beta coefficients across semiconductor companies"

### **Temporal Reasoning**
- "What was NVDA's price trend over the last quarter?"
- "Which companies had unusual trading volume yesterday?"
- "Show me Friday trading patterns for tech stocks"
- "How do stock prices typically behave after earnings announcements?"

### **Causal Analysis**  
- "What factors caused NVDA's price surge in 2024?"
- "How does high trading volume correlate with price movements?"
- "What market conditions lead to tech stock volatility?"
- "Why do AI stocks move together during market events?"

### **Comparative Analysis**
- "Compare the financial metrics of NVDA vs AMD"
- "Which companies have the most stable dividend yields?"
- "Rank tech companies by market capitalization"
- "Show me the most volatile stocks in the AI sector"

### **Sector Analysis**
- "What are the characteristics of AI semiconductor companies?"
- "How do cloud companies compare to traditional tech?"
- "Which sectors show the strongest growth patterns?"
- "What defines a high-growth tech company?"

## Data Flow Architecture

```
Google Sheets (GOOGLEFINANCE data)
    ↓ Google Sheets API v4
Financial Data Processor (Python)
    ↓ Semantic structuring + metadata
Sutra Bulk Ingester (Rust)
    ↓ TCP binary protocol  
Sutra Storage Server (Rust)
    ↓ Unified learning pipeline
Sutra Core Engine (Python)
    ↓ Semantic reasoning
Query Interfaces:
    • Web UI (React) - http://localhost:3000
    • REST API - http://localhost:8000  
    • Python Client Library
    • Direct TCP protocol
```

## Monitoring & Validation

### Check Ingestion Success
```bash
# View ingestion logs
docker logs sutra-works-bulk-ingester

# Check storage statistics  
curl http://localhost:8000/api/v1/stats

# Validate learning with test queries
python examples/financial_data/test_financial_learning.py
```

### Performance Metrics
- **Ingestion Rate**: 100-200 concepts/second
- **Query Response**: <100ms for simple queries  
- **Storage Efficiency**: ~2KB per financial data point
- **Memory Usage**: ~1GB for 10K financial concepts

### Troubleshooting

**Common Issues:**

1. **Google Sheets API Errors**
   ```bash
   # Check API key and sheet permissions
   python examples/financial_ingester.py --config my_config.json --dry-run
   ```

2. **Sutra Connection Issues**
   ```bash
   # Verify Sutra services are running
   sutra status
   curl http://localhost:8000/health
   ```

3. **Empty Query Results**
   ```bash
   # Check if data was ingested
   curl http://localhost:8000/api/v1/stats
   # Re-run ingestion if needed
   ```

## Next Steps

1. **Expand Data Sources**: Add more sheets, companies, timeframes
2. **Custom Metrics**: Add calculated fields (RSI, moving averages, etc.)
3. **Automation**: Set up scheduled ingestion for real-time updates
4. **Advanced Queries**: Explore complex multi-step reasoning
5. **Integration**: Connect to trading platforms, alerts, dashboards

## Success Validation

Your integration is successful when you can:

✅ Query current stock prices and get accurate responses  
✅ Ask temporal questions about price trends and patterns  
✅ Perform causal analysis of market movements  
✅ Compare companies across multiple financial metrics  
✅ Get explanations for Sutra's reasoning and conclusions  

The financial data is now part of Sutra's knowledge graph and available for semantic reasoning across the entire platform!