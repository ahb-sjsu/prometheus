#!/bin/bash
# Publish script for prometheus-analyzer to PyPI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default to test PyPI
PYPI_SERVER="${1:-test}"

if [ "$PYPI_SERVER" = "test" ]; then
    PYPI_URL="https://test.pypi.org/legacy/"
    PYPI_NAME="TestPyPI"
    echo -e "${YELLOW}📦 Publishing to TestPyPI...${NC}"
elif [ "$PYPI_SERVER" = "prod" ] || [ "$PYPI_SERVER" = "production" ]; then
    PYPI_URL="https://upload.pypi.org/legacy/"
    PYPI_NAME="PyPI"
    echo -e "${GREEN}🚀 Publishing to Production PyPI...${NC}"
else
    echo -e "${RED}❌ Invalid server. Use 'test' or 'prod'${NC}"
    echo "Usage: $0 [test|prod]"
    exit 1
fi

# Check if build artifacts exist
if [ ! -d "dist" ] || [ -z "$(ls -A dist/)" ]; then
    echo -e "${YELLOW}⚠️  No build artifacts found. Building first...${NC}"
    ./build.sh
fi

# Check if twine is installed
if ! command -v twine &> /dev/null; then
    echo -e "${YELLOW}⚠️  twine not found. Installing...${NC}"
    pip install twine
fi

# Check credentials
if [ -z "$TWINE_USERNAME" ] || [ -z "$TWINE_PASSWORD" ]; then
    echo -e "${YELLOW}⚠️  TWINE_USERNAME and TWINE_PASSWORD not set.${NC}"
    echo "You can set them as environment variables or twine will prompt you."
    echo ""
    echo "For TestPyPI, create an account at: https://test.pypi.org/account/register/"
    echo "For PyPI, create an account at: https://pypi.org/account/register/"
    echo ""
    read -p "Press Enter to continue..."
fi

# Upload to PyPI
echo -e "${GREEN}Uploading to ${PYPI_NAME}...${NC}"
twine upload \
    --repository-url "$PYPI_URL" \
    dist/*

echo ""
echo -e "${GREEN}✅ Successfully published to ${PYPI_NAME}!${NC}"
echo ""

if [ "$PYPI_SERVER" = "test" ]; then
    echo "Test installation with:"
    echo "  pip install --index-url https://test.pypi.org/simple/ prometheus-analyzer"
    echo ""
    echo "When ready for production, run:"
    echo "  ./publish.sh prod"
else
    echo "Install with:"
    echo "  pip install prometheus-analyzer"
fi

