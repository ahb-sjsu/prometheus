#!/bin/bash
# Build script for prometheus-analyzer package

set -e

echo "🔨 Building prometheus-analyzer package..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build the package
echo "Building wheel and source distribution..."
python -m build

echo "✅ Build complete! Distributions are in dist/"
ls -lh dist/

