#!/bin/bash
# Context Garden Sync - Quick Setup Script
# Run this to initialize context sync for your repositories

set -e

echo "🌿 Context Garden Sync Setup"
echo "=============================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo -e "${BLUE}✓ Python 3 found${NC}"

# Make script executable
chmod +x context-sync.py
echo -e "${BLUE}✓ Made context-sync.py executable${NC}"

# Copy example config if config doesn't exist
if [ ! -f sync_config.json ]; then
    if [ -f sync_config.example.json ]; then
        cp sync_config.example.json sync_config.json
        echo -e "${YELLOW}⚠️  Copied sync_config.example.json to sync_config.json${NC}"
        echo -e "${YELLOW}⚠️  EDIT sync_config.json before running sync!${NC}"
    fi
fi

echo -e "${GREEN}="
echo "Setup complete! Next steps:"
echo "="
echo ""
echo "1. Edit your configuration:"
echo "   vim sync_config.json"
echo ""
echo "2. Test with dry-run:"
echo "   python3 context-sync.py --dry-run"
echo ""
echo "3. Run sync:"
echo "   python3 context-sync.py"
echo ""
echo "4. For offline mode:"
echo "   python3 context-sync.py --offline"
echo "   (when back online)"
echo "   python3 context-sync.py --sync-queue"
echo ""
echo "Documentation: CONTEXT_SYNC_README.md"
echo -e "${GREEN}${NC}"
