#!/bin/bash

# EvoLabeler Cross-Platform Build Script
# Supports building macOS and Windows installers

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Parse command line arguments
BUILD_MAC=false
BUILD_WIN=false
BUILD_ALL=false

# Default: build all platforms
if [ $# -eq 0 ]; then
    BUILD_ALL=true
else
    while [[ $# -gt 0 ]]; do
        case $1 in
            --mac)
                BUILD_MAC=true
                shift
                ;;
            --win)
                BUILD_WIN=true
                shift
                ;;
            --all)
                BUILD_ALL=true
                shift
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                echo "Usage: $0 [--mac] [--win] [--all]"
                echo "  --mac: Build macOS only"
                echo "  --win: Build Windows only"
                echo "  --all: Build all platforms (default)"
                exit 1
                ;;
        esac
    done
fi

# If no specific platform selected, build all
if [ "$BUILD_ALL" = true ]; then
    BUILD_MAC=true
    BUILD_WIN=true
fi

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   EvoLabeler Cross-Platform Build Script       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Detect current platform
CURRENT_OS=$(uname -s)
CURRENT_ARCH=$(uname -m)

echo -e "${CYAN}📋 Build Configuration:${NC}"
echo -e "   Current OS: ${CURRENT_OS}"
echo -e "   Current Arch: ${CURRENT_ARCH}"
echo -e "   Build macOS: ${BUILD_MAC}"
echo -e "   Build Windows: ${BUILD_WIN}"
echo ""

# Step 1: Clean previous builds (保留 Logo.png)
echo -e "${YELLOW}🧹 Step 1/6: Cleaning previous builds...${NC}"

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
echo -e "${YELLOW}🎨 Step 2/6: Creating app icons...${NC}"
if [ -f "./create-icons.sh" ]; then
    ./create-icons.sh
    echo -e "${GREEN}   ✓ Icons created${NC}"
else
    echo -e "${YELLOW}   ⚠️  Icon script not found, skipping...${NC}"
fi
echo ""

# Step 3: Build frontend
echo -e "${YELLOW}🔨 Step 3/6: Building frontend with Vite...${NC}"
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

# Step 4: Check architecture (for macOS builds)
MAC_ARCH=""
if [ "$BUILD_MAC" = true ]; then
    echo -e "${YELLOW}🖥️  Step 4/6: Detecting macOS architecture...${NC}"
    if [ "$CURRENT_OS" = "Darwin" ]; then
        if [ "$CURRENT_ARCH" = "arm64" ]; then
            echo -e "${GREEN}   ✓ Apple Silicon (M1/M2/M3) detected${NC}"
            MAC_ARCH="arm64"
        else
            echo -e "${GREEN}   ✓ Intel (x64) detected${NC}"
            MAC_ARCH="x64"
        fi
    else
        echo -e "${YELLOW}   ⚠️  Not on macOS, will build universal macOS app${NC}"
        MAC_ARCH="x64,arm64"
    fi
    echo ""
fi

# Step 5: Build macOS app
if [ "$BUILD_MAC" = true ]; then
    echo -e "${YELLOW}🍎 Step 5/6: Building macOS app...${NC}"
    echo -e "${BLUE}   This may take a few minutes...${NC}"
    
    if [ -n "$MAC_ARCH" ]; then
        npx electron-builder --mac --${MAC_ARCH} 2>&1 | grep -E "(building|packaging|completed|DMG)" || true
    else
        npx electron-builder --mac 2>&1 | grep -E "(building|packaging|completed|DMG)" || true
    fi
    
    echo -e "${GREEN}   ✓ macOS build complete${NC}"
    echo ""
fi

# Step 6: Build Windows app
if [ "$BUILD_WIN" = true ]; then
    echo -e "${YELLOW}🪟 Step 6/6: Building Windows app...${NC}"
    echo -e "${BLUE}   This may take a few minutes...${NC}"
    echo -e "${YELLOW}   ⚠️  Note: Windows build on macOS requires Wine for NSIS${NC}"
    echo -e "${YELLOW}   If Wine is not installed, the build may fail${NC}"
    echo ""
    
    # Check if Wine is available (optional but helpful)
    if command -v wine &> /dev/null; then
        echo -e "${GREEN}   ✓ Wine detected, NSIS installer will be built${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Wine not found. Installing via Homebrew recommended:${NC}"
        echo -e "${CYAN}      brew install --cask wine-stable${NC}"
        echo -e "${YELLOW}   Continuing anyway...${NC}"
    fi
    echo ""
    
    # Build Windows installer
    npx electron-builder --win --x64 2>&1 | grep -E "(building|packaging|completed|NSIS)" || true
    
    echo -e "${GREEN}   ✓ Windows build complete${NC}"
    echo ""
fi

# Summary
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        Build Complete! 🎉                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Show output location
if [ -d "release" ]; then
    echo -e "${BLUE}📂 Build output in 'release' folder:${NC}"
    echo ""
    
    # macOS outputs
    if [ "$BUILD_MAC" = true ]; then
        echo -e "${CYAN}🍎 macOS Installers:${NC}"
        ls -lh release/*.dmg 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}' || echo -e "   ${YELLOW}No DMG files found${NC}"
        echo ""
    fi
    
    # Windows outputs
    if [ "$BUILD_WIN" = true ]; then
        echo -e "${CYAN}🪟 Windows Installers:${NC}"
        ls -lh release/*.exe 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}' || echo -e "   ${YELLOW}No EXE files found${NC}"
        echo ""
    fi
    
    # Show total size
    TOTAL_SIZE=$(du -sh release 2>/dev/null | cut -f1)
    echo -e "${GREEN}✅ Total build size: ${TOTAL_SIZE}${NC}"
    echo ""
    
    # Installation instructions
    echo -e "${BLUE}════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Installation Instructions:${NC}"
    echo ""
    
    if [ "$BUILD_MAC" = true ]; then
        echo -e "${CYAN}🍎 macOS:${NC}"
        echo -e "  1. Open release/EvoLabeler-*.dmg"
        echo -e "  2. Drag EvoLabeler to Applications"
        echo -e "  3. Launch from Applications folder"
        echo ""
    fi
    
    if [ "$BUILD_WIN" = true ]; then
        echo -e "${CYAN}🪟 Windows:${NC}"
        echo -e "  1. Run release/EvoLabeler Setup *.exe"
        echo -e "  2. Follow the installation wizard"
        echo -e "  3. Launch from Start Menu or Desktop shortcut"
        echo ""
    fi
    
    echo -e "${BLUE}════════════════════════════════════════════════${NC}"
else
    echo -e "${RED}❌ Build failed - release folder not found${NC}"
    exit 1
fi

echo ""
