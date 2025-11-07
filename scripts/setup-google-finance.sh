#!/bin/bash

# Google Finance to Sutra AI Setup Script
# This script helps you set up bulk ingestion of Google Finance data into Sutra

set -e

echo "🚀 Google Finance to Sutra AI Setup"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Sutra is running
check_sutra() {
    echo -e "${BLUE}Checking Sutra services...${NC}"
    
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✅ Sutra API is running${NC}"
    else
        echo -e "${YELLOW}⚠️  Sutra API not detected on localhost:8000${NC}"
        echo "Please start Sutra first:"
        echo "  SUTRA_EDITION=simple sutra deploy"
        echo ""
    fi
    
    if nc -z localhost 7000 2>/dev/null; then
        echo -e "${GREEN}✅ Sutra Storage is running${NC}"
    else
        echo -e "${YELLOW}⚠️  Sutra Storage not detected on localhost:7000${NC}"
    fi
}

# Setup Google API credentials
setup_google_api() {
    echo -e "${BLUE}Setting up Google API access...${NC}"
    echo ""
    echo "To use Google Sheets GOOGLEFINANCE data, you need:"
    echo "1. A Google Cloud Project with Sheets API enabled"
    echo "2. An API key for authentication"
    echo ""
    echo "Get your API key from:"
    echo "👉 https://console.cloud.google.com/apis/credentials"
    echo ""
    
    read -p "Do you have a Google API key? (y/n): " has_key
    
    if [[ $has_key =~ ^[Yy]$ ]]; then
        read -p "Enter your Google API key: " api_key
        
        # Update config files with API key
        if [[ ! -z "$api_key" ]]; then
            sed -i.bak "s/YOUR_GOOGLE_API_KEY_HERE/$api_key/g" examples/financial_data/basic_config.json
            sed -i.bak "s/YOUR_GOOGLE_API_KEY_HERE/$api_key/g" examples/financial_data/historical_config.json
            echo -e "${GREEN}✅ API key configured${NC}"
        fi
    else
        echo -e "${YELLOW}Please get your API key first, then run this script again${NC}"
        exit 1
    fi
}

# Create sample Google Sheet
create_sample_sheet() {
    echo -e "${BLUE}Setting up sample Google Sheet...${NC}"
    echo ""
    echo "Sample Google Sheets template:"
    echo "📊 https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    echo ""
    echo "To create your own sheet:"
    echo "1. Make a copy of the sample sheet"
    echo "2. Add GOOGLEFINANCE formulas for your target companies"
    echo "3. Make the sheet publicly readable (Share > Anyone with link can view)"
    echo "4. Copy the sheet ID from the URL"
    echo ""
    
    read -p "Enter your Google Sheets ID (or press Enter to use sample): " sheet_id
    
    if [[ ! -z "$sheet_id" ]]; then
        sed -i.bak "s/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/$sheet_id/g" examples/financial_data/basic_config.json
        echo -e "${GREEN}✅ Sheet ID configured${NC}"
    else
        echo -e "${YELLOW}Using sample sheet (limited data)${NC}"
    fi
}

# Install dependencies
install_dependencies() {
    echo -e "${BLUE}Installing dependencies...${NC}"
    
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✅ Python 3 found${NC}"
    else
        echo -e "${RED}❌ Python 3 is required${NC}"
        exit 1
    fi
    
    # Install Python dependencies
    pip3 install aiohttp pandas tabulate requests > /dev/null 2>&1
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
}

# Test the setup
test_setup() {
    echo -e "${BLUE}Testing the setup...${NC}"
    
    # Test configuration
    echo "Running dry-run test..."
    if python3 examples/financial_ingester.py --config examples/financial_data/basic_config.json --dry-run; then
        echo -e "${GREEN}✅ Configuration test passed${NC}"
    else
        echo -e "${RED}❌ Configuration test failed${NC}"
        echo "Please check your API key and sheet configuration"
        exit 1
    fi
}

# Run ingestion
run_ingestion() {
    echo -e "${BLUE}Running financial data ingestion...${NC}"
    
    read -p "Proceed with data ingestion? (y/n): " proceed
    
    if [[ $proceed =~ ^[Yy]$ ]]; then
        echo "Starting ingestion (this may take a few minutes)..."
        python3 examples/financial_ingester.py --config examples/financial_data/basic_config.json
        
        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}🎉 Financial data ingestion completed!${NC}"
            echo ""
            echo "You can now query Sutra about financial data:"
            echo "  'What was NVDA's price yesterday?'"
            echo "  'Compare tech stock performance'"
            echo "  'Show me high-volume trading days'"
        else
            echo -e "${RED}❌ Ingestion failed${NC}"
            exit 1
        fi
    else
        echo "Ingestion skipped. You can run it manually later:"
        echo "  python3 examples/financial_ingester.py --config examples/financial_data/basic_config.json"
    fi
}

# Validate learning
validate_learning() {
    echo -e "${BLUE}Validating Sutra's financial learning...${NC}"
    
    read -p "Run learning validation tests? (y/n): " validate
    
    if [[ $validate =~ ^[Yy]$ ]]; then
        python3 examples/financial_data/test_financial_learning.py --quick-test
        echo ""
        echo "For comprehensive validation:"
        echo "  python3 examples/financial_data/test_financial_learning.py"
    fi
}

# Main menu
main_menu() {
    echo ""
    echo "What would you like to do?"
    echo "1. Full setup (API + Sheet + Ingestion)"
    echo "2. Configure API key only"
    echo "3. Test current configuration"
    echo "4. Run ingestion with current config"
    echo "5. Validate learning capabilities"
    echo "6. Exit"
    echo ""
    
    read -p "Choose option (1-6): " choice
    
    case $choice in
        1)
            check_sutra
            install_dependencies
            setup_google_api
            create_sample_sheet
            test_setup
            run_ingestion
            validate_learning
            ;;
        2)
            setup_google_api
            ;;
        3)
            test_setup
            ;;
        4)
            run_ingestion
            ;;
        5)
            validate_learning
            ;;
        6)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid option"
            main_menu
            ;;
    esac
}

# Welcome message
echo ""
echo "This script will help you:"
echo "• Configure Google Sheets API access"
echo "• Set up GOOGLEFINANCE data extraction"
echo "• Bulk ingest financial data into Sutra"
echo "• Validate Sutra's financial reasoning capabilities"
echo ""

# Check if we're in the right directory
if [[ ! -f "sutra" ]]; then
    echo -e "${RED}❌ Please run this script from the Sutra project root directory${NC}"
    exit 1
fi

# Create directories if they don't exist
mkdir -p examples/financial_data

main_menu

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Query Sutra about financial data through the web UI (http://localhost:3000)"
echo "2. Use the API to ask complex financial questions"
echo "3. Explore temporal and causal relationships in stock data"
echo ""
echo "Example queries to try:"
echo "  'What caused NVDA to surge in 2024?'"
echo "  'Compare trading volumes across tech companies'"
echo "  'Which stocks show the most volatility?'"
echo "  'What patterns exist in quarterly earnings announcements?'"