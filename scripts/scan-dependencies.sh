#!/bin/bash
# Local Dependency Scanning Script for Sutra Models
# Run without Docker to quickly check dependencies and vulnerabilities

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    Sutra Models Dependency Scanner    ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check for required tools
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${YELLOW}Warning: $1 not installed. Install with: $2${NC}"
        return 1
    fi
    return 0
}

# Summary variables
TOTAL_PYTHON_DEPS=0
TOTAL_RUST_DEPS=0
TOTAL_NODE_DEPS=0
TOTAL_VULNS=0
CRITICAL_VULNS=0
HIGH_VULNS=0

# Create reports directory
REPORT_DIR="dependency-reports-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$REPORT_DIR"

echo -e "${BLUE}📁 Reports will be saved to: $REPORT_DIR${NC}"
echo ""

# Python dependency scanning
echo -e "${BLUE}🐍 Scanning Python Dependencies...${NC}"
if check_tool "pip-audit" "pip install pip-audit"; then
    PYTHON_REPORT="$REPORT_DIR/python-dependencies.txt"
    echo "# Python Dependency Report" > "$PYTHON_REPORT"
    echo "Generated: $(date)" >> "$PYTHON_REPORT"
    echo "" >> "$PYTHON_REPORT"
    
    # Find all Python dependency files
    for req_file in $(find . -name "requirements*.txt" -o -name "pyproject.toml" | grep -v node_modules | grep -v venv); do
        echo -e "  Scanning: $req_file"
        echo "## $req_file" >> "$PYTHON_REPORT"
        
        if [[ $req_file == *.txt ]]; then
            # Count dependencies
            dep_count=$(grep -v '^#' "$req_file" | grep -v '^$' | wc -l)
            TOTAL_PYTHON_DEPS=$((TOTAL_PYTHON_DEPS + dep_count))
            echo "Dependencies: $dep_count" >> "$PYTHON_REPORT"
            
            # Run pip-audit
            pip-audit -r "$req_file" --format json 2>/dev/null > "$REPORT_DIR/$(basename $req_file .txt)-audit.json" || true
            
            # Parse vulnerabilities
            if [ -f "$REPORT_DIR/$(basename $req_file .txt)-audit.json" ]; then
                vuln_count=$(jq '.vulnerabilities | length' "$REPORT_DIR/$(basename $req_file .txt)-audit.json" 2>/dev/null || echo 0)
                if [ "$vuln_count" -gt 0 ]; then
                    echo -e "    ${RED}⚠️  Found $vuln_count vulnerabilities${NC}"
                    echo "Vulnerabilities: $vuln_count" >> "$PYTHON_REPORT"
                    TOTAL_VULNS=$((TOTAL_VULNS + vuln_count))
                    
                    # Count critical/high
                    critical=$(jq '[.vulnerabilities[] | select(.severity == "CRITICAL")] | length' "$REPORT_DIR/$(basename $req_file .txt)-audit.json" 2>/dev/null || echo 0)
                    high=$(jq '[.vulnerabilities[] | select(.severity == "HIGH")] | length' "$REPORT_DIR/$(basename $req_file .txt)-audit.json" 2>/dev/null || echo 0)
                    CRITICAL_VULNS=$((CRITICAL_VULNS + critical))
                    HIGH_VULNS=$((HIGH_VULNS + high))
                else
                    echo -e "    ${GREEN}✅ No vulnerabilities found${NC}"
                    echo "Vulnerabilities: 0" >> "$PYTHON_REPORT"
                fi
            fi
        fi
        echo "" >> "$PYTHON_REPORT"
    done
    
    # Check for outdated packages
    echo -e "  Checking for outdated packages..."
    pip list --outdated --format json > "$REPORT_DIR/python-outdated.json" 2>/dev/null || true
    outdated_count=$(jq '. | length' "$REPORT_DIR/python-outdated.json" 2>/dev/null || echo 0)
    echo -e "  Found ${YELLOW}$outdated_count${NC} outdated Python packages"
else
    echo -e "${YELLOW}  Skipping Python scanning (pip-audit not installed)${NC}"
fi
echo ""

# Rust dependency scanning
echo -e "${BLUE}🦀 Scanning Rust Dependencies...${NC}"
if check_tool "cargo" "install rust via rustup.rs"; then
    RUST_REPORT="$REPORT_DIR/rust-dependencies.txt"
    echo "# Rust Dependency Report" > "$RUST_REPORT"
    echo "Generated: $(date)" >> "$RUST_REPORT"
    echo "" >> "$RUST_REPORT"
    
    # Check if cargo-audit is installed
    if check_tool "cargo-audit" "cargo install cargo-audit"; then
        for cargo_file in $(find . -name "Cargo.toml" | grep -v node_modules | grep -v target); do
            dir=$(dirname "$cargo_file")
            echo -e "  Scanning: $cargo_file"
            echo "## $cargo_file" >> "$RUST_REPORT"
            
            # Count dependencies
            if [ -f "$dir/Cargo.lock" ]; then
                dep_count=$(grep -c '^\[\[package\]\]' "$dir/Cargo.lock" 2>/dev/null || echo 0)
                TOTAL_RUST_DEPS=$((TOTAL_RUST_DEPS + dep_count))
                echo "Dependencies: $dep_count" >> "$RUST_REPORT"
                
                # Run cargo-audit
                cd "$dir"
                cargo audit --json 2>/dev/null > "$REPORT_DIR/$(basename $dir)-rust-audit.json" || true
                cd - > /dev/null
                
                # Parse vulnerabilities
                if [ -f "$REPORT_DIR/$(basename $dir)-rust-audit.json" ]; then
                    # cargo-audit JSON format is different
                    vuln_count=$(jq '.vulnerabilities.list | length' "$REPORT_DIR/$(basename $dir)-rust-audit.json" 2>/dev/null || echo 0)
                    if [ "$vuln_count" -gt 0 ]; then
                        echo -e "    ${RED}⚠️  Found $vuln_count vulnerabilities${NC}"
                        echo "Vulnerabilities: $vuln_count" >> "$RUST_REPORT"
                        TOTAL_VULNS=$((TOTAL_VULNS + vuln_count))
                    else
                        echo -e "    ${GREEN}✅ No vulnerabilities found${NC}"
                        echo "Vulnerabilities: 0" >> "$RUST_REPORT"
                    fi
                fi
            else
                echo -e "    ${YELLOW}No Cargo.lock file (run 'cargo build' first)${NC}"
            fi
            echo "" >> "$RUST_REPORT"
        done
    else
        echo -e "${YELLOW}  Skipping vulnerability scan (cargo-audit not installed)${NC}"
    fi
    
    # Check for outdated crates
    if check_tool "cargo-outdated" "cargo install cargo-outdated"; then
        echo -e "  Checking for outdated crates..."
        cargo outdated --format json > "$REPORT_DIR/rust-outdated.json" 2>/dev/null || true
    fi
else
    echo -e "${YELLOW}  Skipping Rust scanning (cargo not installed)${NC}"
fi
echo ""

# Node.js dependency scanning
echo -e "${BLUE}📦 Scanning Node.js Dependencies...${NC}"
if check_tool "npm" "install Node.js from nodejs.org"; then
    NODE_REPORT="$REPORT_DIR/node-dependencies.txt"
    echo "# Node.js Dependency Report" > "$NODE_REPORT"
    echo "Generated: $(date)" >> "$NODE_REPORT"
    echo "" >> "$NODE_REPORT"
    
    for package_file in $(find . -name "package.json" | grep -v node_modules); do
        dir=$(dirname "$package_file")
        echo -e "  Scanning: $package_file"
        echo "## $package_file" >> "$NODE_REPORT"
        
        if [ -f "$dir/package-lock.json" ]; then
            # Count dependencies
            dep_count=$(jq '.dependencies | length' "$package_file" 2>/dev/null || echo 0)
            dev_dep_count=$(jq '.devDependencies | length' "$package_file" 2>/dev/null || echo 0)
            total_deps=$((dep_count + dev_dep_count))
            TOTAL_NODE_DEPS=$((TOTAL_NODE_DEPS + total_deps))
            echo "Dependencies: $dep_count (+ $dev_dep_count dev)" >> "$NODE_REPORT"
            
            # Run npm audit
            cd "$dir"
            npm audit --json 2>/dev/null > "$REPORT_DIR/$(basename $dir)-npm-audit.json" || true
            cd - > /dev/null
            
            # Parse vulnerabilities
            if [ -f "$REPORT_DIR/$(basename $dir)-npm-audit.json" ]; then
                vuln_count=$(jq '.metadata.vulnerabilities.total' "$REPORT_DIR/$(basename $dir)-npm-audit.json" 2>/dev/null || echo 0)
                if [ "$vuln_count" -gt 0 ]; then
                    echo -e "    ${RED}⚠️  Found $vuln_count vulnerabilities${NC}"
                    echo "Vulnerabilities: $vuln_count" >> "$NODE_REPORT"
                    TOTAL_VULNS=$((TOTAL_VULNS + vuln_count))
                    
                    # Count critical/high
                    critical=$(jq '.metadata.vulnerabilities.critical' "$REPORT_DIR/$(basename $dir)-npm-audit.json" 2>/dev/null || echo 0)
                    high=$(jq '.metadata.vulnerabilities.high' "$REPORT_DIR/$(basename $dir)-npm-audit.json" 2>/dev/null || echo 0)
                    CRITICAL_VULNS=$((CRITICAL_VULNS + critical))
                    HIGH_VULNS=$((HIGH_VULNS + high))
                else
                    echo -e "    ${GREEN}✅ No vulnerabilities found${NC}"
                    echo "Vulnerabilities: 0" >> "$NODE_REPORT"
                fi
            fi
            
            # Check for outdated packages
            cd "$dir"
            npm outdated --json > "$REPORT_DIR/$(basename $dir)-npm-outdated.json" 2>/dev/null || true
            cd - > /dev/null
        else
            echo -e "    ${YELLOW}No package-lock.json (run 'npm install' first)${NC}"
        fi
        echo "" >> "$NODE_REPORT"
    done
else
    echo -e "${YELLOW}  Skipping Node.js scanning (npm not installed)${NC}"
fi
echo ""

# License checking (basic)
echo -e "${BLUE}📜 Checking Licenses...${NC}"
LICENSE_REPORT="$REPORT_DIR/license-report.txt"
echo "# License Report" > "$LICENSE_REPORT"
echo "Generated: $(date)" >> "$LICENSE_REPORT"
echo "" >> "$LICENSE_REPORT"

if check_tool "pip-licenses" "pip install pip-licenses"; then
    echo -e "  Checking Python licenses..."
    pip-licenses --format=json --with-license-file > "$REPORT_DIR/python-licenses.json" 2>/dev/null || true
    
    # Check for problematic licenses
    if [ -f "$REPORT_DIR/python-licenses.json" ]; then
        problematic=$(jq '[.[] | select(.License | test("GPL|AGPL|LGPL|SSPL|Commons Clause"))] | length' "$REPORT_DIR/python-licenses.json" 2>/dev/null || echo 0)
        if [ "$problematic" -gt 0 ]; then
            echo -e "    ${YELLOW}⚠️  Found $problematic packages with potentially problematic licenses${NC}"
            echo "## Potentially Problematic Python Licenses" >> "$LICENSE_REPORT"
            jq -r '.[] | select(.License | test("GPL|AGPL|LGPL|SSPL|Commons Clause")) | "\(.Name): \(.License)"' "$REPORT_DIR/python-licenses.json" >> "$LICENSE_REPORT"
        else
            echo -e "    ${GREEN}✅ No problematic licenses found${NC}"
        fi
    fi
fi
echo ""

# Generate summary
echo -e "${BLUE}📊 Summary Report${NC}"
echo "========================================="
SUMMARY_REPORT="$REPORT_DIR/SUMMARY.md"
{
    echo "# Dependency Scan Summary"
    echo "Generated: $(date)"
    echo ""
    echo "## Statistics"
    echo "- Python Dependencies: $TOTAL_PYTHON_DEPS"
    echo "- Rust Dependencies: $TOTAL_RUST_DEPS"
    echo "- Node.js Dependencies: $TOTAL_NODE_DEPS"
    echo "- **Total Dependencies: $((TOTAL_PYTHON_DEPS + TOTAL_RUST_DEPS + TOTAL_NODE_DEPS))**"
    echo ""
    echo "## Vulnerabilities"
    echo "- Critical: $CRITICAL_VULNS"
    echo "- High: $HIGH_VULNS"
    echo "- **Total: $TOTAL_VULNS**"
    echo ""
    
    if [ "$CRITICAL_VULNS" -gt 0 ]; then
        echo "### ⚠️ CRITICAL VULNERABILITIES DETECTED!"
        echo "Review the detailed reports for more information."
    elif [ "$HIGH_VULNS" -gt 0 ]; then
        echo "### ⚠️ High severity vulnerabilities detected"
        echo "Consider updating affected packages."
    elif [ "$TOTAL_VULNS" -gt 0 ]; then
        echo "### ℹ️ Some vulnerabilities detected"
        echo "Review and prioritize updates as needed."
    else
        echo "### ✅ No vulnerabilities detected"
        echo "All dependencies appear to be secure."
    fi
} > "$SUMMARY_REPORT"

cat "$SUMMARY_REPORT"
echo ""
echo -e "${GREEN}Reports saved to: $REPORT_DIR/${NC}"
echo ""

# Optional: Open report directory
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${BLUE}Opening report directory...${NC}"
    open "$REPORT_DIR"
fi

# Exit with error if critical vulnerabilities found
if [ "$CRITICAL_VULNS" -gt 0 ]; then
    exit 1
fi

exit 0