# Google Sheets Financial Data Template for Sutra AI

This directory contains templates and examples for ingesting financial data from Google Sheets into Sutra AI.

## Quick Setup Guide

### 1. Create Google Sheets with GOOGLEFINANCE Formulas

1. **Create a new Google Sheet**
2. **Copy the formulas below** into your sheet
3. **Get your Google API key** from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
4. **Make your sheet publicly readable** (Share > Anyone with the link can view)

### 2. Google Sheets Template

Copy this structure into your Google Sheet:

#### Sheet: "FinancialData"

| A (Date) | B (Ticker) | C (Price) | D (Volume) | E (Market Cap) | F (P/E Ratio) | G (Dividend Yield) | H (Beta) |
|----------|------------|-----------|------------|----------------|---------------|-------------------|----------|
| Date | Ticker | Price | Volume | Market Cap | P/E Ratio | Dividend Yield | Beta |
| 2025-11-07 | NVDA | =GOOGLEFINANCE("NVDA","price") | =GOOGLEFINANCE("NVDA","volume") | =GOOGLEFINANCE("NVDA","marketcap") | =GOOGLEFINANCE("NVDA","pe") | =GOOGLEFINANCE("NVDA","dividendyield") | =GOOGLEFINANCE("NVDA","beta") |
| 2025-11-07 | GOOGL | =GOOGLEFINANCE("GOOGL","price") | =GOOGLEFINANCE("GOOGL","volume") | =GOOGLEFINANCE("GOOGL","marketcap") | =GOOGLEFINANCE("GOOGL","pe") | =GOOGLEFINANCE("GOOGL","dividendyield") | =GOOGLEFINANCE("GOOGL","beta") |
| 2025-11-07 | MSFT | =GOOGLEFINANCE("MSFT","price") | =GOOGLEFINANCE("MSFT","volume") | =GOOGLEFINANCE("MSFT","marketcap") | =GOOGLEFINANCE("MSFT","pe") | =GOOGLEFINANCE("MSFT","dividendyield") | =GOOGLEFINANCE("MSFT","beta") |

### 3. Historical Data Template (Advanced)

For historical data, use this more sophisticated approach:

#### Sheet: "HistoricalData"

| A (Date) | B (Ticker) | C (Price) | D (Volume) | E (High) | F (Low) | G (Close) |
|----------|------------|-----------|------------|----------|---------|-----------|
| Date | Ticker | Price | Volume | High | Low | Close |
| =DATE(2024,1,1) | NVDA | =INDEX(GOOGLEFINANCE("NVDA","price",DATE(2024,1,1),DATE(2024,1,1),"DAILY"),2,2) | =INDEX(GOOGLEFINANCE("NVDA","volume",DATE(2024,1,1),DATE(2024,1,1),"DAILY"),2,2) | =INDEX(GOOGLEFINANCE("NVDA","high",DATE(2024,1,1),DATE(2024,1,1),"DAILY"),2,2) | =INDEX(GOOGLEFINANCE("NVDA","low",DATE(2024,1,1),DATE(2024,1,1),"DAILY"),2,2) | =INDEX(GOOGLEFINANCE("NVDA","close",DATE(2024,1,1),DATE(2024,1,1),"DAILY"),2,2) |

### 4. Bulk Historical Data Formula (Recommended)

For bulk historical data, use this single formula in cell A1:

```
=GOOGLEFINANCE("NVDA","all",DATE(2024,1,1),DATE(2025,11,7),"DAILY")
```

This will populate multiple rows automatically. Then add ticker column manually or use this formula in column A:

```
=IF(ROW()=1,"Ticker",IF(B2<>"","NVDA",""))
```

## Top AI/Tech Companies for Analysis

Here are the recommended tickers for AI and technology analysis:

### AI & Semiconductors
- **NVDA** - NVIDIA Corporation
- **AMD** - Advanced Micro Devices
- **INTC** - Intel Corporation  
- **QCOM** - Qualcomm Incorporated
- **AVGO** - Broadcom Inc.

### Big Tech
- **GOOGL** - Alphabet Inc. (Google)
- **MSFT** - Microsoft Corporation
- **AAPL** - Apple Inc.
- **AMZN** - Amazon.com Inc.
- **META** - Meta Platforms Inc.

### Cloud & Enterprise Software
- **CRM** - Salesforce Inc.
- **NOW** - ServiceNow Inc.
- **ORCL** - Oracle Corporation
- **ADBE** - Adobe Inc.
- **SNOW** - Snowflake Inc.

### AI-Focused Companies
- **PLTR** - Palantir Technologies
- **AI** - C3.ai Inc.
- **MDB** - MongoDB Inc.
- **NET** - Cloudflare Inc.
- **ZS** - Zscaler Inc.

### Electric Vehicles & Innovation
- **TSLA** - Tesla Inc.
- **RIVN** - Rivian Automotive
- **LCID** - Lucid Group Inc.

## GOOGLEFINANCE Function Reference

### Available Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `"price"` | Current stock price | `=GOOGLEFINANCE("NVDA","price")` |
| `"volume"` | Trading volume | `=GOOGLEFINANCE("NVDA","volume")` |
| `"marketcap"` | Market capitalization | `=GOOGLEFINANCE("NVDA","marketcap")` |
| `"pe"` | Price-to-earnings ratio | `=GOOGLEFINANCE("NVDA","pe")` |
| `"eps"` | Earnings per share | `=GOOGLEFINANCE("NVDA","eps")` |
| `"high"` | Day's high price | `=GOOGLEFINANCE("NVDA","high")` |
| `"low"` | Day's low price | `=GOOGLEFINANCE("NVDA","low")` |
| `"open"` | Opening price | `=GOOGLEFINANCE("NVDA","open")` |
| `"close"` | Closing price | `=GOOGLEFINANCE("NVDA","close")` |
| `"dividendyield"` | Dividend yield | `=GOOGLEFINANCE("NVDA","dividendyield")` |
| `"beta"` | Beta coefficient | `=GOOGLEFINANCE("NVDA","beta")` |
| `"52weekhigh"` | 52-week high | `=GOOGLEFINANCE("NVDA","52weekhigh")` |
| `"52weeklow"` | 52-week low | `=GOOGLEFINANCE("NVDA","52weeklow")` |

### Historical Data Syntax

```
=GOOGLEFINANCE(ticker, attribute, start_date, end_date, interval)
```

**Parameters:**
- `ticker`: Stock symbol (e.g., "NVDA")
- `attribute`: Data type (e.g., "price", "volume")
- `start_date`: Start date (e.g., DATE(2024,1,1))
- `end_date`: End date (e.g., DATE(2025,11,7))
- `interval`: "DAILY" or "WEEKLY"

**Example:**
```
=GOOGLEFINANCE("NVDA","price",DATE(2024,1,1),DATE(2025,11,7),"DAILY")
```

## Sample Configuration Files

### basic_config.json
```json
{
  "spreadsheet_id": "YOUR_SHEET_ID_HERE",
  "sheet_name": "FinancialData",
  "range": "A1:H1000",
  "api_key": "YOUR_API_KEY_HERE",
  "target_companies": ["NVDA", "GOOGL", "MSFT", "TSLA", "AAPL"],
  "batch_size": 100,
  "enable_temporal_reasoning": true,
  "enable_causal_analysis": true
}
```

### historical_config.json
```json
{
  "spreadsheet_id": "YOUR_SHEET_ID_HERE", 
  "sheet_name": "HistoricalData",
  "range": "A1:Z10000",
  "api_key": "YOUR_API_KEY_HERE",
  "target_companies": [
    "NVDA", "GOOGL", "MSFT", "TSLA", "AAPL", "AMZN", "META",
    "CRM", "NOW", "ORCL", "ADBE", "SNOW", "PLTR", "AI"
  ],
  "start_date": "2024-01-01",
  "end_date": "2025-11-07",
  "batch_size": 200,
  "max_concepts_per_company": 2000,
  "enable_temporal_reasoning": true,
  "enable_causal_analysis": true
}
```

## Usage Examples

### 1. Basic Current Data Ingestion
```bash
python examples/financial_ingester.py \
  --sheet-id "1ABC123XYZ..." \
  --api-key "AIza..." \
  --companies "NVDA,GOOGL,MSFT,TSLA,AAPL"
```

### 2. Historical Data Range
```bash
python examples/financial_ingester.py \
  --config historical_config.json \
  --start-date "2024-01-01" \
  --end-date "2025-11-07"
```

### 3. Dry Run (Test Configuration)
```bash
python examples/financial_ingester.py \
  --sheet-id "1ABC123XYZ..." \
  --api-key "AIza..." \
  --dry-run
```

## Expected Sutra Learning Outcomes

After ingesting financial data, Sutra will be able to answer queries like:

### Temporal Reasoning
- "What was NVDA's price trend from January to October 2024?"
- "Which companies had the highest trading volume on Fridays?"
- "Show me the quarterly performance patterns for tech stocks"

### Causal Analysis  
- "What factors caused NVDA's price surge in 2024?"
- "How does high trading volume correlate with price movements?"
- "What market conditions led to tech stock volatility?"

### Comparative Analysis
- "Compare the P/E ratios of AI companies vs traditional tech"
- "Which companies have the most stable beta coefficients?"
- "Show me dividend yield trends across the tech sector"

### Predictive Insights
- "Based on historical patterns, what drives TSLA volatility?"
- "Which companies show seasonal trading patterns?"
- "What are the leading indicators for tech stock performance?"

## Troubleshooting

### Common Issues

1. **GOOGLEFINANCE returns #N/A**
   - Check ticker symbol spelling
   - Verify the attribute is supported for that stock
   - Some attributes may not be available for all stocks

2. **API Rate Limits**
   - Reduce batch_size in configuration
   - Add delays between requests
   - Use Google Sheets caching by refreshing data periodically

3. **Missing Historical Data**
   - GOOGLEFINANCE has limited historical range
   - Some data may not be available for newer companies
   - Consider using multiple date ranges

4. **Sheet Permission Errors**
   - Ensure sheet is publicly readable
   - Verify API key has Sheets API enabled
   - Check spreadsheet ID is correct

### Performance Tips

1. **Optimize Sheet Layout**
   - Put date ranges in separate sheets
   - Use array formulas for bulk data
   - Cache static company information

2. **Batch Processing**
   - Process data in chunks of 100-500 rows
   - Use date-based batching for historical data
   - Monitor Sutra storage server performance

3. **Data Quality**
   - Filter out weekends/holidays
   - Handle missing values gracefully
   - Validate ticker symbols before processing

## Advanced Integration

### Custom Formulas for Enhanced Learning

Add these calculated columns for richer semantic content:

```
# Price Change %
=IF(C2<>"",(C2-C1)/C1*100,"")

# Volume vs Average
=IF(D2<>"",D2/AVERAGE(D:D),"")

# Market Category
=IF(E2>1000000000000,"Large Cap",IF(E2>200000000000,"Mid Cap","Small Cap"))

# Volatility Indicator  
=IF(AND(F2<>"",F2>0),IF(F2>1.5,"High Volatility",IF(F2<0.8,"Low Volatility","Normal")),"")
```

This creates rich semantic relationships that Sutra can learn and reason about!