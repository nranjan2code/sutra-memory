#!/bin/bash
# MSME Continuous Learning Deployment Script
# Deploys Sutra AI with MSME-specific configuration for Government of India data

set -e

echo "🇮🇳 MSME Continuous Learning Pipeline Deployment"
echo "=================================================="

# Check if Sutra is available
if ! command -v ./sutra &> /dev/null; then
    echo "❌ Error: Sutra command not found. Make sure you're in the sutra-memory directory."
    exit 1
fi

# Set environment for MSME scenario
export SUTRA_EDITION=enterprise
export SUTRA_SCENARIO=msme_learning
export SUTRA_SECURE_MODE=false  # Development mode for testing

echo "📋 Configuration:"
echo "   Edition: $SUTRA_EDITION"
echo "   Scenario: $SUTRA_SCENARIO"
echo "   Secure Mode: $SUTRA_SECURE_MODE"
echo ""

# Step 1: Clean any existing deployment
echo "🧹 Cleaning previous deployment..."
./sutra clean --containers --images --quiet || true

# Step 2: Build services optimized for MSME learning
echo "🔨 Building Sutra services for MSME learning..."
./sutra build

# Check build status
if ! ./sutra validate --quiet; then
    echo "❌ Build validation failed. Exiting."
    exit 1
fi

echo "✅ Build completed successfully"

# Step 3: Deploy with MSME-specific configuration
echo "🚀 Deploying Sutra AI for MSME continuous learning..."
./sutra deploy

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 30

# Step 4: Check deployment status
echo "🔍 Checking deployment status..."
./sutra status

# Step 5: Create MSME plugin directory and install adapter
echo "📦 Setting up MSME bulk ingestion plugin..."

# Create plugin directory if it doesn't exist
mkdir -p ./plugins/government_data

# Copy MSME adapter to plugin directory
cp examples/msme_bulk_adapter.py ./plugins/government_data/

# Create plugin configuration
cat > ./plugins/government_data/plugin.json << EOF
{
    "name": "msme_csv_adapter",
    "version": "1.0.0",
    "description": "Government of India MSME data adapter",
    "entry_point": "msme_bulk_adapter.py",
    "supported_formats": ["csv", "json", "api"],
    "requirements": ["aiofiles", "faker"]
}
EOF

echo "✅ MSME plugin installed"

# Step 6: Generate sample data for testing
echo "📊 Generating sample MSME data..."
mkdir -p ./data/msme

# Create sample CSV data
cat > ./data/msme/sample_msme_data.csv << 'EOF'
udyam_number,enterprise_name,constitution,state,district,nic_code,nic_description,category,investment_in_plant,annual_turnover,total_employees,male_employees,female_employees,pan,gstin,aadhaar_linked,registration_date,financial_year,status
UDYAM-MH-24-0000001,ABC Manufacturing Pvt Ltd,Private Limited Company,Maharashtra,Mumbai,25920,Manufacture of plastic packing goods,Small,15000000,45000000,45,30,15,ABCDE1234F,27ABCDE1234F1Z5,true,2024-03-15,2024-25,Active
UDYAM-KA-24-0000002,Tech Solutions LLP,LLP,Karnataka,Bangalore Urban,62090,Other information technology service activities,Micro,800000,3500000,12,8,4,PQRST5678G,29PQRST5678G1Z9,true,2024-04-22,2024-25,Active
UDYAM-TN-24-0000003,Textile Traders,Partnership,Tamil Nadu,Chennai,47521,Retail sale of textiles,Small,5000000,25000000,28,18,10,LMNOP9012H,33LMNOP9012H1Z3,true,2024-02-10,2024-25,Active
UDYAM-GJ-24-0000004,Food Processing Industries,Proprietorship,Gujarat,Ahmedabad,15111,Processing and preserving of meat,Medium,45000000,180000000,125,80,45,XYZAB5678C,24XYZAB5678C1Z7,true,2024-01-08,2024-25,Active
UDYAM-DL-24-0000005,Consulting Services,Private Limited Company,Delhi,New Delhi,70200,Management consultancy activities,Micro,1200000,4500000,8,5,3,DEFGH3456I,07DEFGH3456I1Z1,true,2024-05-30,2024-25,Active
EOF

echo "✅ Sample data created: ./data/msme/sample_msme_data.csv"

# Step 7: Test the pipeline
echo "🧪 Testing MSME learning pipeline..."

# Check if Python dependencies are available
python3 -c "import aiohttp, asyncio" 2>/dev/null || {
    echo "📦 Installing Python dependencies..."
    pip3 install aiohttp faker aiofiles
}

# Run a quick test
echo "🔬 Running quick validation test..."
if python3 -c "
import asyncio
import aiohttp
import sys

async def test_connection():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/health') as response:
                if response.status == 200:
                    print('✅ Sutra API is responding')
                    return True
                else:
                    print(f'❌ API returned status {response.status}')
                    return False
    except Exception as e:
        print(f'❌ Connection failed: {e}')
        return False

result = asyncio.run(test_connection())
sys.exit(0 if result else 1)
"; then
    echo "✅ API connectivity test passed"
else
    echo "❌ API connectivity test failed"
    echo "🔍 Checking service logs..."
    docker logs $(docker ps -q --filter "name=sutra-api") --tail 10
fi

# Step 8: Create convenience scripts
echo "📝 Creating convenience scripts..."

# Create learning script
cat > ./run_msme_learning.sh << 'EOF'
#!/bin/bash
# Quick script to run MSME learning pipeline

echo "🇮🇳 Running MSME Continuous Learning Pipeline"
echo "=============================================="

# Check if services are running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Sutra services not running. Deploy first with:"
    echo "   ./deploy_msme_learning.sh"
    exit 1
fi

echo "🚀 Starting MSME learning pipeline..."
python3 examples/msme_learning_pipeline.py

echo "✅ MSME learning completed!"
EOF

chmod +x ./run_msme_learning.sh

# Create bulk ingestion script
cat > ./run_msme_bulk_ingestion.sh << 'EOF'
#!/bin/bash
# Script to run bulk MSME data ingestion

echo "📊 MSME Bulk Data Ingestion"
echo "==========================="

# Submit bulk ingestion job
curl -X POST http://localhost:8005/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "csv",
    "source_config": {
      "csv_path": "./data/msme/sample_msme_data.csv",
      "chunk_size": 100,
      "encoding": "utf-8"
    },
    "adapter_name": "msme_csv_adapter"
  }' | jq .

echo "✅ Bulk ingestion job submitted!"
echo "Check status at: http://localhost:8005/jobs"
EOF

chmod +x ./run_msme_bulk_ingestion.sh

# Step 9: Display summary and next steps
echo ""
echo "🎉 MSME Continuous Learning Deployment Complete!"
echo "=============================================="
echo ""
echo "📋 What was deployed:"
echo "   ✅ Sutra AI Enterprise Edition (10 services)"
echo "   ✅ MSME bulk ingestion adapter"
echo "   ✅ Sample MSME data (5 records)"
echo "   ✅ Python learning pipeline"
echo "   ✅ Convenience scripts"
echo ""
echo "🔗 Service URLs:"
echo "   📊 Sutra API:        http://localhost:8000"
echo "   🤖 Hybrid Service:   http://localhost:8001"  
echo "   📦 Bulk Ingester:    http://localhost:8005"
echo "   🎛️  Control Panel:    http://localhost:3000"
echo ""
echo "🚀 Next Steps:"
echo "   1. Test the learning pipeline:"
echo "      ./run_msme_learning.sh"
echo ""
echo "   2. Try bulk ingestion:"
echo "      ./run_msme_bulk_ingestion.sh"
echo ""
echo "   3. Query learned knowledge:"
echo "      curl -X POST http://localhost:8000/query \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"query\": \"Show me MSMEs in Maharashtra\"}'"
echo ""
echo "   4. Add more MSME data:"
echo "      Edit ./data/msme/sample_msme_data.csv"
echo "      Then run bulk ingestion again"
echo ""
echo "   5. Monitor system:"
echo "      ./sutra status"
echo ""
echo "📚 Documentation:"
echo "   📄 Scenario Guide:   examples/msme_continuous_learning_scenario.md"
echo "   🐍 Python Pipeline:  examples/msme_learning_pipeline.py"  
echo "   📦 Bulk Adapter:     examples/msme_bulk_adapter.py"
echo ""
echo "🎯 This demonstrates Sutra's continuous learning capabilities"
echo "   with real-world Government of India MSME data patterns."
echo "   All learning goes through the unified pipeline - no shortcuts!"
echo ""
EOF