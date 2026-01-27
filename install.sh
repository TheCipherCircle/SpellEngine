#!/bin/bash
#
# Cipher Circle Installer
# Installs PatternForge + Storysmith for testing
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_banner() {
    echo -e "${CYAN}"
    echo "    ╔═══════════════════════════════════════════════════╗"
    echo "    ║                                                   ║"
    echo "    ║          THE CIPHER CIRCLE INSTALLER              ║"
    echo "    ║                                                   ║"
    echo "    ║     PatternForge + Storysmith + Dread Citadel     ║"
    echo "    ║                                                   ║"
    echo "    ╚═══════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

# Default install directory
INSTALL_DIR="${CIPHER_CIRCLE_DIR:-$HOME/cipher-circle}"

print_banner

echo ""
print_info "Install directory: $INSTALL_DIR"
print_info "Set CIPHER_CIRCLE_DIR to change this"
echo ""

# Check prerequisites
print_step "Checking prerequisites..."

# Python 3.10+
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    print_error "Python 3.10+ required (found $PYTHON_VERSION)"
    exit 1
fi
print_success "Python $PYTHON_VERSION"

# Git
if ! command -v git &> /dev/null; then
    print_error "Git not found. Please install git"
    exit 1
fi
print_success "Git available"

# pip
if ! python3 -m pip --version &> /dev/null; then
    print_error "pip not found. Please install pip"
    exit 1
fi
print_success "pip available"

echo ""

# Create install directory
print_step "Creating install directory..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"
print_success "Created $INSTALL_DIR"

# Clone or update PatternForge
print_step "Setting up PatternForge..."
if [ -d "PatternForge" ]; then
    print_info "PatternForge exists, updating..."
    cd PatternForge
    git pull
    cd ..
else
    print_info "Cloning PatternForge..."
    git clone git@github.com:TheCipherCircle/PatternForge.git
fi
print_success "PatternForge ready"

# Clone or update Storysmith
print_step "Setting up Storysmith..."
if [ -d "Storysmith" ]; then
    print_info "Storysmith exists, updating..."
    cd Storysmith
    git pull
    cd ..
else
    print_info "Cloning Storysmith..."
    git clone git@github.com:TheCipherCircle/Storysmith.git
fi
print_success "Storysmith ready"

# Create virtual environment
print_step "Creating virtual environment..."
cd PatternForge
if [ -d ".venv" ]; then
    print_info "Virtual environment exists, reusing..."
else
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate
print_success "Virtual environment activated"

# Install PatternForge
print_step "Installing PatternForge..."
pip install -e . --quiet
print_success "PatternForge installed"

# Install Storysmith
print_step "Installing Storysmith..."
cd ../Storysmith
pip install -e . --quiet
print_success "Storysmith installed"

# Install pygame
print_step "Installing pygame..."
pip install pygame --quiet
print_success "pygame installed"

echo ""

# Verify installation
print_step "Verifying installation..."

if python3 -c "import patternforge" 2>/dev/null; then
    print_success "PatternForge imports OK"
else
    print_error "PatternForge import failed"
    exit 1
fi

if python3 -c "import storysmith" 2>/dev/null; then
    print_success "Storysmith imports OK"
else
    print_error "Storysmith import failed"
    exit 1
fi

if python3 -c "import pygame" 2>/dev/null; then
    print_success "pygame imports OK"
else
    print_error "pygame import failed"
    exit 1
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}                 INSTALLATION COMPLETE                   ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo "To play the game:"
echo ""
echo -e "  ${CYAN}cd $INSTALL_DIR/PatternForge${NC}"
echo -e "  ${CYAN}source .venv/bin/activate${NC}"
echo -e "  ${CYAN}python3 -m storysmith play dread_citadel${NC}"
echo ""
echo "Or run:"
echo ""
echo -e "  ${CYAN}$INSTALL_DIR/PatternForge/.venv/bin/python3 -m storysmith play dread_citadel${NC}"
echo ""
echo -e "${CYAN}May your hashes crack swiftly.${NC}"
echo ""
