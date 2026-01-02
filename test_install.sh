#!/bin/bash
# Test installation script for prometheus-analyzer

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PYPI_SERVER="${1:-test}"

if [ "$PYPI_SERVER" = "test" ]; then
    # Use TestPyPI for the package, but regular PyPI for dependencies
    PYPI_INDEX="--index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/"
    PYPI_NAME="TestPyPI"
    echo -e "${YELLOW}🧪 Testing installation from TestPyPI...${NC}"
    echo -e "${YELLOW}   (dependencies will be fetched from regular PyPI)${NC}"
elif [ "$PYPI_SERVER" = "prod" ] || [ "$PYPI_SERVER" = "production" ]; then
    PYPI_INDEX=""
    PYPI_NAME="PyPI"
    echo -e "${GREEN}🧪 Testing installation from Production PyPI...${NC}"
else
    echo -e "${RED}❌ Invalid server. Use 'test' or 'prod'${NC}"
    echo "Usage: $0 [test|prod]"
    exit 1
fi

# Create a temporary virtual environment
TEST_DIR=$(mktemp -d)
echo "Creating test environment in: $TEST_DIR"

cd "$TEST_DIR"
python3 -m venv test_env
source test_env/bin/activate

# Install the package
echo -e "${GREEN}Installing prometheus-analyzer from ${PYPI_NAME}...${NC}"
pip install --upgrade pip
pip install $PYPI_INDEX prometheus-analyzer

# Test that commands are available
echo ""
echo -e "${GREEN}Testing installed commands...${NC}"

commands=("prometheus" "olympus" "hubris")
for cmd in "${commands[@]}"; do
    if command -v "$cmd" &> /dev/null; then
        echo -e "  ✅ $cmd is available"
        $cmd --help > /dev/null 2>&1 && echo -e "     (help works)" || echo -e "     (help check skipped)"
    else
        echo -e "  ${RED}❌ $cmd not found${NC}"
    fi
done

# Test Python import
echo ""
echo -e "${GREEN}Testing Python imports...${NC}"
python3 -c "import prometheus; print('✅ prometheus module imports')" 2>&1 || echo -e "${RED}❌ prometheus import failed${NC}"
python3 -c "import olympus; print('✅ olympus module imports')" 2>&1 || echo -e "${RED}❌ olympus import failed${NC}"
python3 -c "import hubris; print('✅ hubris module imports')" 2>&1 || echo -e "${RED}❌ hubris import failed${NC}"

# Cleanup
deactivate
cd -
rm -rf "$TEST_DIR"

echo ""
echo -e "${GREEN}✅ Test complete!${NC}"

