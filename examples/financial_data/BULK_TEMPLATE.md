# Google Sheets Bulk Historical Data Template

## Overview

This template is designed for bulk ingestion of historical financial data for 100+ companies into Sutra AI. It uses optimized GOOGLEFINANCE formulas to extract maximum data efficiently.

## Sheet Structure for Bulk Historical Data

### Method 1: Single Company Historical Data (Recommended)

Create separate sheets for each company or use this formula structure:

```
=GOOGLEFINANCE("NVDA","all",DATE(2022,1,1),DATE(2025,11,7),"DAILY")
```

This single formula will populate:
- Column A: Date
- Column B: Open
- Column C: High  
- Column D: Low
- Column E: Close
- Column F: Volume

### Method 2: Multi-Company Current Data

For current/recent data across multiple companies:

| A | B | C | D | E | F | G | H | I | J |
|---|---|---|---|---|---|---|---|---|---|
| Date | Ticker | Price | Volume | Market Cap | P/E | High | Low | Open | Close |
| =TODAY() | NVDA | =GOOGLEFINANCE("NVDA","price") | =GOOGLEFINANCE("NVDA","volume") | =GOOGLEFINANCE("NVDA","marketcap") | =GOOGLEFINANCE("NVDA","pe") | =GOOGLEFINANCE("NVDA","high") | =GOOGLEFINANCE("NVDA","low") | =GOOGLEFINANCE("NVDA","open") | =GOOGLEFINANCE("NVDA","close") |
| =TODAY() | GOOGL | =GOOGLEFINANCE("GOOGL","price") | =GOOGLEFINANCE("GOOGL","volume") | =GOOGLEFINANCE("GOOGL","marketcap") | =GOOGLEFINANCE("GOOGL","pe") | =GOOGLEFINANCE("GOOGL","high") | =GOOGLEFINANCE("GOOGL","low") | =GOOGLEFINANCE("GOOGL","open") | =GOOGLEFINANCE("GOOGL","close") |

### Method 3: Bulk Historical Template (Most Efficient)

Create this structure for maximum data extraction:

```
Sheet: BulkHistoricalData
Range: A1:Z50000

Formula in A1:
=ARRAYFORMULA(QUERY(
  FLATTEN(
    {
      GOOGLEFINANCE("NVDA","all",DATE(2022,1,1),DATE(2025,11,7),"DAILY");
      GOOGLEFINANCE("GOOGL","all",DATE(2022,1,1),DATE(2025,11,7),"DAILY");
      GOOGLEFINANCE("MSFT","all",DATE(2022,1,1),DATE(2025,11,7),"DAILY")
    }
  ),
  "SELECT * WHERE Col1 IS NOT NULL"
))
```

## Complete Bulk Setup Instructions

### Step 1: Create Master Historical Data Sheet

1. **Create new Google Sheet**
2. **Name it**: "Sutra_Financial_Bulk_Data"
3. **Create sheets for each data type**:
   - Sheet1: "NVDA_Historical"
   - Sheet2: "GOOGL_Historical" 
   - Sheet3: "MSFT_Historical"
   - etc.

### Step 2: Add Bulk Historical Formulas

For each company sheet, use this formula in cell A1:

```
=GOOGLEFINANCE("NVDA","all",DATE(2020,1,1),DATE(2025,11,7),"DAILY")
```

Replace "NVDA" with the appropriate ticker symbol.

### Step 3: Combined Data Sheet

Create a "CombinedData" sheet with this structure:

| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| Date | Ticker | Open | High | Low | Close | Volume |

Use this formula to combine all company data:

```
=ARRAYFORMULA(QUERY(
  {
    QUERY(NVDA_Historical!A2:F,"SELECT *, 'NVDA' WHERE A IS NOT NULL",0);
    QUERY(GOOGL_Historical!A2:F,"SELECT *, 'GOOGL' WHERE A IS NOT NULL",0);
    QUERY(MSFT_Historical!A2:F,"SELECT *, 'MSFT' WHERE A IS NOT NULL",0)
  },
  "SELECT Col1, Col7, Col2, Col3, Col4, Col5, Col6 ORDER BY Col1 DESC"
))
```

## Top 100 AI/Tech Companies List

For comprehensive coverage, include these companies in your bulk data:

### Tier 1: Core AI/Tech (20 companies)
```
NVDA, AMD, INTC, QCOM, GOOGL, MSFT, AAPL, AMZN, META, TSLA,
CRM, ORCL, NOW, ADBE, SNOW, PLTR, AI, NFLX, IBM, CSCO
```

### Tier 2: Cloud/SaaS (25 companies)  
```
MDB, NET, ZS, OKTA, CRWD, DDOG, SPLK, WORK, TEAM, WDAY,
VEEV, TWLO, DOCU, ZM, BILL, SHOP, SQ, PYPL, COIN, HOOD,
AFRM, UPST, MELI, SE, RBLX
```

### Tier 3: Semiconductors (20 companies)
```
TSM, ASML, LRCX, KLAC, AMAT, ADI, TXN, MRVL, MU, NXPI,
ON, SWKS, MPWR, MCHP, XLNX, AVGO, ALTR, CDNA, AMBA, ROKU
```

### Tier 4: Emerging/Growth (20 companies)
```
PATH, U, GTLB, S, FROG, BBAI, SOUN, RIVN, LCID, BROS,
RKLB, SPCE, OPEN, SOFI, LMND, ROOT, PANW, FTNT, CYBR, TENB
```

### Tier 5: Additional Tech (15 companies)
```
DELL, HPE, VRNS, RPD, QLYS, FEYE, CHKP, PFPT, ATLX, SEND,
GTLB, RXRX, GPLV, SOUN, BBAI
```

## Bulk Data Formulas by Category

### Historical Price Data (5 years)
```
=GOOGLEFINANCE("TICKER","all",DATE(2020,1,1),DATE(2025,11,7),"DAILY")
```

### Financial Metrics
```
=GOOGLEFINANCE("TICKER","pe")           // P/E Ratio
=GOOGLEFINANCE("TICKER","marketcap")    // Market Cap
=GOOGLEFINANCE("TICKER","beta")         // Beta
=GOOGLEFINANCE("TICKER","eps")          // Earnings Per Share
=GOOGLEFINANCE("TICKER","dividendyield") // Dividend Yield
=GOOGLEFINANCE("TICKER","52weekhigh")   // 52-Week High
=GOOGLEFINANCE("TICKER","52weeklow")    // 52-Week Low
```

### Volume and Volatility Data
```
=GOOGLEFINANCE("TICKER","volume",DATE(2024,1,1),DATE(2025,11,7),"DAILY")
=GOOGLEFINANCE("TICKER","high",DATE(2024,1,1),DATE(2025,11,7),"DAILY")
=GOOGLEFINANCE("TICKER","low",DATE(2024,1,1),DATE(2025,11,7),"DAILY")
```

## Performance Optimization Tips

### 1. Sheet Structure
- **Separate sheets per company** for better performance
- **Limit to 10,000 rows per sheet** to avoid timeouts
- **Use date ranges** rather than full history

### 2. Formula Optimization
```
// Good - Specific date range
=GOOGLEFINANCE("NVDA","all",DATE(2024,1,1),DATE(2024,12,31),"DAILY")

// Better - Smaller chunks for bulk processing  
=GOOGLEFINANCE("NVDA","all",DATE(2024,1,1),DATE(2024,6,30),"DAILY")
```

### 3. Batch Processing
- **Process 10-20 companies at a time**
- **Use separate config files** for different batches
- **Monitor Google Sheets API quotas**

## Bulk Ingestion Commands

### Process All Companies (Full Dataset)
```bash
python examples/bulk_financial_ingester.py \
  --config examples/financial_data/bulk_config.json \
  --bulk-mode \
  --batch-size 2000
```

### Process by Batches
```bash
# Batch 1: Core AI/Tech
python examples/bulk_financial_ingester.py \
  --companies "NVDA,AMD,GOOGL,MSFT,AAPL,AMZN,META,TSLA,CRM,ORCL" \
  --start-date "2022-01-01" \
  --batch-size 1000 \
  --bulk-mode

# Batch 2: Cloud/SaaS  
python examples/bulk_financial_ingester.py \
  --companies "NOW,ADBE,SNOW,MDB,NET,ZS,OKTA,CRWD,DDOG,SPLK" \
  --start-date "2022-01-01" \
  --batch-size 1000 \
  --bulk-mode
```

### Monitor Progress
```bash
# Check Sutra storage stats
curl -s http://localhost:8080/api/stats | jq

# Check bulk ingester status
docker logs sutra-works-bulk-ingester | tail -20
```

## Expected Results

After bulk ingestion, you'll have:

### Data Volume
- **~100 companies** × **1,000 data points** = **100,000+ financial concepts**
- **~3 years** of daily historical data per company
- **Rich semantic relationships** between companies, dates, and metrics

### Query Capabilities
```
"Compare the volatility of AI semiconductor companies vs cloud companies in 2024"
"Which companies showed the strongest correlation during the March 2024 market correction?"
"What patterns emerge in Q4 earnings announcements across tech sectors?"
"Show me companies that outperformed the market during AI boom periods"
"Which factors drove the semiconductor rally in early 2024?"
```

### Performance Metrics
- **Ingestion rate**: 500-1,000 concepts/second
- **Processing time**: ~2-4 hours for full dataset
- **Storage size**: ~50-100MB for semantic concepts
- **Query response**: <100ms for complex multi-company queries

## Troubleshooting Bulk Ingestion

### Common Issues

1. **Google Sheets API Limits**
   ```bash
   # Reduce batch size and add delays
   python examples/bulk_financial_ingester.py \
     --batch-size 500 \
     --max-concurrent-batches 2
   ```

2. **Memory Issues**
   ```bash
   # Use streaming mode
   python examples/bulk_financial_ingester.py \
     --bulk-mode \
     --memory-limit-mb 8192
   ```

3. **Network Timeouts**
   ```bash
   # Increase timeout and retry logic
   python examples/bulk_financial_ingester.py \
     --batch-size 250 \
     --retry-failed
   ```

This template enables efficient bulk ingestion of comprehensive financial data for sophisticated AI-powered analysis in Sutra!