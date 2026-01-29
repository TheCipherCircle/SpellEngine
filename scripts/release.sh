#!/bin/bash
#
# Quick release builder for SpellEngine
# Reads config from release_config.json if present
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  STORYSMITH RELEASE BUILDER${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""

# Check for Proton Drive
PROTON_PATHS=(
    "$HOME/Proton Drive"
    "$HOME/Library/CloudStorage/ProtonDrive-"*
    "$HOME/ProtonDrive"
)

PROTON_SYNC=""
for path in "${PROTON_PATHS[@]}"; do
    if [ -d "$path" ]; then
        PROTON_SYNC="$path/SpellEngine-Releases"
        break
    fi
done

if [ -z "$PROTON_SYNC" ]; then
    echo -e "${YELLOW}WARNING: Proton Drive not detected${NC}"
    echo "  Install Proton Drive desktop app or specify path manually:"
    echo "  ./scripts/build_release.py --proton-sync /path/to/sync/folder"
    echo ""
    PROTON_ARG=""
else
    echo -e "Proton Drive detected: ${GREEN}$PROTON_SYNC${NC}"
    # Create releases folder if needed
    mkdir -p "$PROTON_SYNC"
    PROTON_ARG="--proton-sync \"$PROTON_SYNC\""
fi

# Parse arguments
VERSION=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Build command
cd "$PROJECT_ROOT"

if [ -n "$VERSION" ]; then
    VERSION_ARG="--version $VERSION"
else
    VERSION_ARG=""
fi

echo ""
echo "Running build..."
echo ""

if [ -n "$PROTON_ARG" ]; then
    python3 scripts/build_release.py $VERSION_ARG $PROTON_ARG
else
    python3 scripts/build_release.py $VERSION_ARG
fi

BUILD_STATUS=$?

if [ $BUILD_STATUS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  BUILD SUCCESSFUL${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"

    if [ -n "$PROTON_SYNC" ] && [ -d "$PROTON_SYNC" ]; then
        echo ""
        echo -e "Proton Drive sync folder: ${GREEN}$PROTON_SYNC${NC}"
        echo "  Files will auto-sync when Proton Drive is running."
        echo ""
        echo "  Share link steps:"
        echo "    1. Open Proton Drive (web or app)"
        echo "    2. Navigate to SpellEngine-Releases"
        echo "    3. Right-click the .zip file → Get link"
        echo "    4. Share the link with testers"
    fi

    echo ""
    echo "Distribution files in: dist/"
    ls -la "$PROJECT_ROOT/dist/"*.zip 2>/dev/null | tail -3
else
    echo ""
    echo -e "${RED}BUILD FAILED${NC}"
    exit 1
fi
