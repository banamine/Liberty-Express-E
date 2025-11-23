#!/bin/bash

# ScheduleFlow Prerequisites Checker
# Verifies all required dependencies before installation

echo "================================"
echo "ScheduleFlow Prerequisites Check"
echo "================================"
echo

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter
PASSED=0
FAILED=0

# Function to check command exists
check_command() {
    if command -v "$1" &> /dev/null; then
        local version=$("$1" "$2" 2>&1 | head -n 1)
        echo -e "${GREEN}✅${NC} $1: $version"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌${NC} $1: NOT FOUND"
        ((FAILED++))
        return 1
    fi
}

# Function to check build tools
check_build_tools() {
    echo
    echo "Checking build tools..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if xcode-select -p >/dev/null 2>&1; then
            echo -e "${GREEN}✅${NC} Xcode Command Line Tools: Found"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠️${NC} Xcode Command Line Tools: NOT FOUND"
            echo "   Run: xcode-select --install"
            ((FAILED++))
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v gcc &> /dev/null; then
            local version=$(gcc --version | head -n 1)
            echo -e "${GREEN}✅${NC} GCC: $version"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠️${NC} GCC: NOT FOUND"
            echo "   Run: sudo apt-get install build-essential"
            ((FAILED++))
        fi
        
        if command -v python3-config &> /dev/null; then
            echo -e "${GREEN}✅${NC} Python dev headers: Found"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠️${NC} Python dev headers: NOT FOUND"
            echo "   Run: sudo apt-get install python3-dev"
            ((FAILED++))
        fi
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        # Windows
        echo -e "${YELLOW}⚠️${NC} Windows detected: Please install Visual C++ Build Tools"
        echo "   Download from: https://visualstudio.microsoft.com/downloads/"
        ((FAILED++))
    fi
}

# Main checks
echo "Essential Requirements:"
echo "======================"

check_command "node" "--version"
check_command "npm" "--version"
check_command "python3" "--version"

check_build_tools

echo
echo "Optional Dependencies:"
echo "======================"

# Check for optional tools
if command -v git &> /dev/null; then
    local version=$(git --version)
    echo -e "${GREEN}✅${NC} git: $version"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️${NC} git: NOT FOUND (needed only for git clone)"
    ((FAILED++))
fi

if command -v curl &> /dev/null; then
    echo -e "${GREEN}✅${NC} curl: Found"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️${NC} curl: NOT FOUND (useful for testing)"
fi

if command -v docker &> /dev/null; then
    local version=$(docker --version)
    echo -e "${GREEN}✅${NC} docker: $version"
    ((PASSED++))
else
    echo -e "${YELLOW}ℹ️${NC} docker: NOT FOUND (optional, for containerization)"
fi

# Summary
echo
echo "================================"
echo "Summary"
echo "================================"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All prerequisites met! Ready to install.${NC}"
    echo
    echo "Next steps:"
    echo "1. npm install"
    echo "2. pip install -r requirements.txt"
    echo "3. python3 test_unit.py"
    echo "4. node api_server.js &"
    echo "5. python3 M3U_Matrix_Pro.py"
    exit 0
else
    echo -e "${RED}❌ Some prerequisites missing.${NC}"
    echo
    echo "Required:"
    echo "  - Node.js v20+"
    echo "  - Python 3.11+"
    echo "  - Build tools (C++ compiler)"
    echo
    echo "See above for installation instructions."
    exit 1
fi
