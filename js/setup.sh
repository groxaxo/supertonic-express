#!/bin/bash

# Setup script for Supertonic TTS JavaScript implementation

echo "=== Supertonic TTS - JavaScript Setup ==="
echo ""

# Check Node.js version
echo "Checking Node.js version..."
NODE_VERSION=$(node -v 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "❌ Node.js is not installed!"
    echo "Please install Node.js >= 18.0.0 from https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js version: $NODE_VERSION"

# Check if version is >= 18
MAJOR_VERSION=$(echo $NODE_VERSION | sed 's/v\([0-9]*\).*/\1/')
if [ "$MAJOR_VERSION" -lt 18 ]; then
    echo "❌ Node.js version must be >= 18.0.0"
    echo "Current version: $NODE_VERSION"
    exit 1
fi

echo ""
echo "Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✓ Setup complete!"
echo ""
echo "To get started:"
echo "  npm run example:basic    # Run basic example"
echo "  npm run example:batch    # Run batch processing example"
echo "  npm run example:advanced # Run multi-language example"
echo ""
echo "For CPU optimization tips, see README.md"
