#!/bin/bash

# EvoLabeler Build Script for macOS
# This script builds the Electron app with proper configuration

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   EvoLabeler Build Script - macOS    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
echo ""

# Step 1: Clean previous builds (保留 Logo.png)
echo -e "${YELLOW}🧹 Step 1/5: Cleaning previous builds...${NC}"

# 备份 Logo.png
if [ -f "../dist/Logo.png" ]; then
    echo -e "${BLUE}   📦 Backing up Logo.png...${NC}"
    cp ../dist/Logo.png /tmp/evolabeler_logo_backup.png
fi

# 清理旧的构建文件
rm -rf ../dist-electron
rm -rf ../release

echo -e "${GREEN}   ✓ Clean complete${NC}"
echo ""

# Step 2: Create icons
echo -e "${YELLOW}🎨 Step 2/5: Creating app icons...${NC}"
if [ -f "./create-icons.sh" ]; then
    ./create-icons.sh
else
    echo -e "${RED}   ⚠️  Icon script not found, skipping...${NC}"
fi
echo ""

# Step 3: Build frontend
echo -e "${YELLOW}🔨 Step 3/5: Building frontend with Vite...${NC}"
cd ..
npm run build 2>&1 | grep -v "DEPRECATION WARNING" || true

# 恢复 Logo.png
if [ -f "/tmp/evolabeler_logo_backup.png" ]; then
    echo -e "${BLUE}   📦 Restoring Logo.png...${NC}"
    cp /tmp/evolabeler_logo_backup.png dist/Logo.png
    rm /tmp/evolabeler_logo_backup.png
fi

echo -e "${GREEN}   ✓ Frontend build complete${NC}"
echo ""

# Step 4: Check architecture
echo -e "${YELLOW}🖥️  Step 4/5: Detecting system architecture...${NC}"
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    echo -e "${GREEN}   ✓ Apple Silicon (M1/M2/M3) detected${NC}"
    BUILD_ARCH="arm64"
else
    echo -e "${GREEN}   ✓ Intel (x64) detected${NC}"
    BUILD_ARCH="x64"
fi
echo ""

# Step 5: Build Electron app
echo -e "${YELLOW}📦 Step 5/5: Building Electron app...${NC}"
echo -e "${BLUE}   This may take a few minutes...${NC}"

# Build with electron-builder
npx electron-builder --mac --$BUILD_ARCH 2>&1 | grep -E "(building|packaging|completed)" || true

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        Build Complete! 🎉            ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════╝${NC}"
echo ""

# Show output location
if [ -d "release" ]; then
    echo -e "${BLUE}📂 Build output:${NC}"
    ls -lh release/*.dmg 2>/dev/null || echo "   DMG file not found"
    echo ""
    echo -e "${GREEN}✅ You can find your app in the 'release' folder${NC}"
    echo -e "${YELLOW}💡 To install: Open the .dmg file and drag EvoLabeler to Applications${NC}"
else
    echo -e "${RED}❌ Build failed - release folder not found${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}  Next steps:${NC}"
echo -e "${BLUE}  1. Open release/EvoLabeler-*.dmg${NC}"
echo -e "${BLUE}  2. Drag EvoLabeler to Applications${NC}"
echo -e "${BLUE}  3. Launch from Applications folder${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

