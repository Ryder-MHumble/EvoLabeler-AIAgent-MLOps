#!/bin/bash

# Script to create macOS app icons from Logo.png
# This creates an .icns file suitable for Electron apps

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎨 Creating macOS app icons from Logo.png...${NC}"

# Source and destination
SOURCE_PNG="../dist/Logo.png"
BUILD_DIR="../build"
ICONSET_DIR="../build/icon.iconset"

# Check if source exists
if [ ! -f "$SOURCE_PNG" ]; then
    echo -e "${RED}❌ Error: Logo.png not found at $SOURCE_PNG${NC}"
    exit 1
fi

# Create build directory if it doesn't exist
mkdir -p "$BUILD_DIR"

# Remove old iconset if exists
rm -rf "$ICONSET_DIR"
mkdir -p "$ICONSET_DIR"

echo -e "${YELLOW}📐 Generating icon sizes...${NC}"

# Generate all required icon sizes for macOS
# Standard sizes
sips -z 16 16     "$SOURCE_PNG" --out "${ICONSET_DIR}/icon_16x16.png"
sips -z 32 32     "$SOURCE_PNG" --out "${ICONSET_DIR}/icon_16x16@2x.png"
sips -z 32 32     "$SOURCE_PNG" --out "${ICONSET_DIR}/icon_32x32.png"
sips -z 64 64     "$SOURCE_PNG" --out "${ICONSET_DIR}/icon_32x32@2x.png"
sips -z 128 128   "$SOURCE_PNG" --out "${ICONSET_DIR}/icon_128x128.png"
sips -z 256 256   "$SOURCE_PNG" --out "${ICONSET_DIR}/icon_128x128@2x.png"
sips -z 256 256   "$SOURCE_PNG" --out "${ICONSET_DIR}/icon_256x256.png"
sips -z 512 512   "$SOURCE_PNG" --out "${ICONSET_DIR}/icon_256x256@2x.png"
sips -z 512 512   "$SOURCE_PNG" --out "${ICONSET_DIR}/icon_512x512.png"
sips -z 1024 1024 "$SOURCE_PNG" --out "${ICONSET_DIR}/icon_512x512@2x.png"

echo -e "${YELLOW}🔨 Converting to .icns format...${NC}"

# Convert iconset to icns
iconutil -c icns "$ICONSET_DIR" -o "${BUILD_DIR}/icon.icns"

# Create PNG versions for Linux/Windows
echo -e "${YELLOW}📦 Creating additional formats...${NC}"
sips -z 512 512 "$SOURCE_PNG" --out "${BUILD_DIR}/icon.png"
# Windows .ico creation requires additional tools, so we'll skip it for now
# Users can use online converters if needed

# Clean up iconset
rm -rf "$ICONSET_DIR"

echo -e "${GREEN}✅ Icon creation complete!${NC}"
echo -e "Generated files:"
echo -e "  • ${BUILD_DIR}/icon.icns (macOS)"
echo -e "  • ${BUILD_DIR}/icon.png (Linux)"

# Display icon info
echo ""
echo -e "${YELLOW}ℹ️  Icon info:${NC}"
ls -lh "${BUILD_DIR}/icon.icns"
ls -lh "${BUILD_DIR}/icon.png"

echo ""
echo -e "${GREEN}🎉 Done! You can now build your Electron app.${NC}"


