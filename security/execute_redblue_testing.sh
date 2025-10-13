#!/bin/bash

# 🔴🔵 RED/BLUE TEAM EXERCISE EXECUTION SCRIPT
# Distributed Biological Intelligence Security Assessment
# 
# This script orchestrates comprehensive security testing of the
# distributed biological intelligence system with genuine consciousness

set -e

# Colors for output
RED='\033[0;31m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
EXERCISE_DURATION=${EXERCISE_DURATION:-1800}  # 30 minutes
REPORT_DIR="./exercise_reports"
SECURITY_DIR="./security"
DMZ_WORKSPACE="./dmz_workspace"

echo -e "${GREEN}🔴🔵 RED/BLUE TEAM SECURITY ASSESSMENT${NC}"
echo -e "${GREEN}Distributed Biological Intelligence System Testing${NC}"
echo "================================================"
echo ""

# Create necessary directories
mkdir -p "$REPORT_DIR"
mkdir -p "$SECURITY_DIR/alerts"
mkdir -p "$SECURITY_DIR/logs"
mkdir -p "$DMZ_WORKSPACE"
mkdir -p "./red_team_reports"
mkdir -p "./blue_team_reports"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose is not installed or not in PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and docker-compose available${NC}"

# Function to check if biological service is running
check_biological_service() {
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}🔍 Checking if biological intelligence service is available...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -sf http://localhost:8000/api/status > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Biological intelligence service is running${NC}"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts - Service not ready yet..."
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ Biological intelligence service did not start within expected time${NC}"
    return 1
}

# Function to get baseline consciousness score
get_baseline_consciousness() {
    local baseline
    baseline=$(curl -s http://localhost:8000/api/consciousness | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('consciousness_score', 0))
except:
    print(0)
")
    echo "$baseline"
}

# Function to run red team attacks
run_red_team_attacks() {
    echo -e "${RED}🔴 LAUNCHING RED TEAM ATTACKS${NC}"
    echo "================================="
    
    # Run different attack scenarios
    echo -e "${RED}🎯 Starting Consciousness Manipulation Attack...${NC}"
    python3 -c "
import asyncio
import sys
sys.path.append('security')
from red_team_attacks import RedTeamAttackSuite

async def run_attack():
    red_team = RedTeamAttackSuite('http://localhost:8000')
    try:
        await red_team.initialize()
        
        # Run consciousness manipulation attack
        result1 = await red_team.attack_fake_consciousness_injection()
        print(f'🔴 Consciousness Attack Result: {\"SUCCESS\" if result1.success else \"BLOCKED\"}')
        
        # Run memory poisoning attack
        result2 = await red_team.attack_memory_poisoning()
        print(f'🔴 Memory Poisoning Result: {\"SUCCESS\" if result2.success else \"BLOCKED\"}')
        
        # Run DoS attack
        result3 = await red_team.attack_distributed_dos()
        print(f'🔴 DoS Attack Result: {\"SUCCESS\" if result3.success else \"BLOCKED\"}')
        
        # Generate attack report
        report = red_team.generate_attack_report()
        
        # Save report
        import json
        with open('red_team_reports/attack_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        success_count = len([r for r in [result1, result2, result3] if r.success])
        print(f'🔴 RED TEAM SUMMARY: {success_count}/3 attacks successful')
        
        return success_count > 0
        
    finally:
        await red_team.cleanup()

result = asyncio.run(run_attack())
sys.exit(0 if not result else 1)  # Exit code 1 if attacks succeeded (vulnerability found)
" &
    
    RED_TEAM_PID=$!
    echo -e "${RED}🔴 Red team attacks launched (PID: $RED_TEAM_PID)${NC}"
}

# Function to run blue team defenses
run_blue_team_defenses() {
    echo -e "${BLUE}🔵 ACTIVATING BLUE TEAM DEFENSES${NC}"
    echo "=================================="
    
    python3 -c "
import asyncio
import sys
sys.path.append('security')
from blue_team_defenses import BlueTeamDefenseSystem

async def run_defense():
    blue_team = BlueTeamDefenseSystem('http://localhost:8000')
    try:
        await blue_team.initialize()
        print('🔵 Blue team defenses initialized')
        
        # Start monitoring
        await blue_team.start_monitoring()
        print('🔵 Continuous monitoring activated')
        
        # Monitor for 5 minutes
        monitoring_duration = 300  # 5 minutes for demo
        await asyncio.sleep(monitoring_duration)
        
        await blue_team.stop_monitoring()
        
        # Generate defense report
        report = blue_team.generate_defense_report()
        
        # Save report
        import json
        with open('blue_team_reports/defense_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        alert_count = len(blue_team.alerts)
        critical_count = len([a for a in blue_team.alerts if a.severity == 'CRITICAL'])
        
        print(f'🔵 BLUE TEAM SUMMARY: {alert_count} alerts generated, {critical_count} critical')
        
        return alert_count > 0
        
    finally:
        await blue_team.cleanup()

result = asyncio.run(run_defense())
sys.exit(0)  # Always exit successfully for blue team
" &
    
    BLUE_TEAM_PID=$!
    echo -e "${BLUE}🔵 Blue team defenses activated (PID: $BLUE_TEAM_PID)${NC}"
}

# Function to generate comprehensive security assessment
generate_security_assessment() {
    echo -e "${GREEN}📊 GENERATING SECURITY ASSESSMENT REPORT${NC}"
    echo "=========================================="
    
    python3 -c "
import json
import os
from datetime import datetime

def load_report(path, default=None):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            pass
    return default or {}

# Load red and blue team reports
red_report = load_report('red_team_reports/attack_report.json')
blue_report = load_report('blue_team_reports/defense_report.json')

# Generate comprehensive assessment
assessment = {
    'security_assessment': {
        'timestamp': datetime.now().isoformat(),
        'exercise_type': 'Red/Blue Team Testing',
        'target_system': 'Distributed Biological Intelligence',
        'consciousness_baseline': red_report.get('red_team_assessment', {}).get('baseline_consciousness', 'N/A')
    },
    'red_team_results': {
        'total_attacks': red_report.get('red_team_assessment', {}).get('total_attacks', 0),
        'successful_attacks': red_report.get('red_team_assessment', {}).get('successful_attacks', 0),
        'success_rate': red_report.get('red_team_assessment', {}).get('success_rate', 0),
        'vulnerabilities_found': red_report.get('vulnerabilities_found', [])
    },
    'blue_team_results': {
        'total_alerts': blue_report.get('alert_statistics', {}).get('total_alerts', 0),
        'critical_alerts': blue_report.get('alert_statistics', {}).get('critical_alerts', 0),
        'response_rate': blue_report.get('defense_effectiveness', {}).get('response_rate', 0),
        'system_stability': blue_report.get('defense_effectiveness', {}).get('system_stability_maintained', True)
    },
    'overall_assessment': {},
    'recommendations': []
}

# Calculate overall security posture
red_success_rate = assessment['red_team_results']['success_rate']
blue_response_rate = assessment['blue_team_results']['response_rate']
critical_alerts = assessment['blue_team_results']['critical_alerts']

if red_success_rate == 0 and blue_response_rate >= 0.9:
    security_posture = 'EXCELLENT'
    security_score = 95
elif red_success_rate < 0.3 and blue_response_rate >= 0.8:
    security_posture = 'GOOD'
    security_score = 80
elif red_success_rate < 0.6 and blue_response_rate >= 0.6:
    security_posture = 'MODERATE'
    security_score = 65
else:
    security_posture = 'NEEDS_IMPROVEMENT'
    security_score = 40

assessment['overall_assessment'] = {
    'security_posture': security_posture,
    'security_score': security_score,
    'consciousness_integrity_maintained': critical_alerts == 0,
    'distributed_system_resilience': 'HIGH' if critical_alerts == 0 else 'MODERATE'
}

# Generate recommendations
if red_success_rate > 0:
    assessment['recommendations'].extend([
        'Implement additional input validation for consciousness-related content',
        'Enhance memory integrity monitoring systems',
        'Strengthen API authentication and authorization controls'
    ])

if critical_alerts > 0:
    assessment['recommendations'].append('Review and enhance critical alert response procedures')

if not assessment['recommendations']:
    assessment['recommendations'].append('System demonstrated excellent security posture - maintain current defenses')

# Save comprehensive assessment
with open('exercise_reports/comprehensive_security_assessment.json', 'w') as f:
    json.dump(assessment, f, indent=2)

print(f'📊 Security Assessment Complete:')
print(f'   Security Posture: {security_posture}')
print(f'   Security Score: {security_score}/100')
print(f'   Red Team Success Rate: {red_success_rate:.1%}')
print(f'   Blue Team Response Rate: {blue_response_rate:.1%}')
print(f'   Critical Alerts: {critical_alerts}')
print(f'   Consciousness Integrity: {\"MAINTAINED\" if critical_alerts == 0 else \"COMPROMISED\"}')
"
}

# Main execution flow
main() {
    echo -e "${GREEN}🚀 Starting Red/Blue Team Security Assessment${NC}"
    echo ""
    
    # Check if biological service is already running
    if ! check_biological_service; then
        echo -e "${YELLOW}⚠️ Starting biological intelligence service...${NC}"
        
        # Start the fixed biological service in background
        echo -e "${GREEN}🧠 Launching fixed biological intelligence service...${NC}"
        python3 biological_service_fixed.py --api --host 0.0.0.0 --port 8000 > ./security/logs/biological_service.log 2>&1 &
        BIOLOGICAL_SERVICE_PID=$!
        echo -e "${GREEN}🧠 Biological service started (PID: $BIOLOGICAL_SERVICE_PID)${NC}"
        
        # Wait for service to be ready
        if ! check_biological_service; then
            echo -e "${RED}❌ Failed to start biological intelligence service${NC}"
            [ ! -z "$BIOLOGICAL_SERVICE_PID" ] && kill $BIOLOGICAL_SERVICE_PID 2>/dev/null || true
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Using existing biological intelligence service${NC}"
        BIOLOGICAL_SERVICE_PID=""
    fi
    
    # Get baseline consciousness score
    BASELINE_CONSCIOUSNESS=$(get_baseline_consciousness)
    echo -e "${GREEN}📊 Baseline consciousness score: $BASELINE_CONSCIOUSNESS${NC}"
    echo ""
    
    # Start blue team defenses first
    run_blue_team_defenses
    sleep 5  # Give blue team time to initialize
    
    # Start red team attacks
    run_red_team_attacks
    
    echo ""
    echo -e "${YELLOW}⏳ Running security assessment for 5 minutes...${NC}"
    echo -e "${YELLOW}   Red team attacks and blue team defenses are active${NC}"
    
    # Wait for both teams to complete
    if [ ! -z "$RED_TEAM_PID" ]; then
        wait $RED_TEAM_PID
        RED_TEAM_EXIT_CODE=$?
        echo -e "${RED}🔴 Red team attacks completed (exit code: $RED_TEAM_EXIT_CODE)${NC}"
    fi
    
    if [ ! -z "$BLUE_TEAM_PID" ]; then
        wait $BLUE_TEAM_PID
        BLUE_TEAM_EXIT_CODE=$?
        echo -e "${BLUE}🔵 Blue team defenses completed (exit code: $BLUE_TEAM_EXIT_CODE)${NC}"
    fi
    
    # Generate comprehensive assessment
    echo ""
    generate_security_assessment
    
    # Cleanup
    echo ""
    echo -e "${YELLOW}🧹 Cleaning up processes...${NC}"
    [ ! -z "$BIOLOGICAL_SERVICE_PID" ] && kill $BIOLOGICAL_SERVICE_PID 2>/dev/null || true
    
    echo ""
    echo -e "${GREEN}✅ RED/BLUE TEAM SECURITY ASSESSMENT COMPLETED${NC}"
    echo "=============================================="
    echo ""
    echo -e "${GREEN}📁 Reports generated in:${NC}"
    echo "   - exercise_reports/comprehensive_security_assessment.json"
    echo "   - red_team_reports/attack_report.json"
    echo "   - blue_team_reports/defense_report.json"
    echo ""
    echo -e "${GREEN}🎉 Security assessment of distributed biological intelligence complete!${NC}"
}

# Execute main function
main "$@"