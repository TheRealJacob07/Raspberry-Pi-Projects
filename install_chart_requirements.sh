#!/bin/bash

# Hailo AI People Counter - Chart Requirements Installer
# =====================================================
#
# This script installs the required Python packages for the chart generator.
# It supports both pip and conda environments.
#
# Usage: ./install_chart_requirements.sh [pip|conda]
# Default: pip

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    local python_cmd="$1"
    local version=$($python_cmd --version 2>&1 | cut -d' ' -f2)
    local major=$(echo $version | cut -d'.' -f1)
    local minor=$(echo $version | cut -d'.' -f2)
    
    if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 7 ]); then
        print_error "Python 3.7 or higher is required. Found: $version"
        return 1
    fi
    
    print_success "Python version: $version"
    return 0
}

# Function to install with pip
install_with_pip() {
    print_status "Installing requirements with pip..."
    
    # Check if pip is available
    if ! command_exists pip; then
        print_error "pip is not installed or not in PATH"
        print_status "Please install pip first: https://pip.pypa.io/en/stable/installation/"
        exit 1
    fi
    
    # Upgrade pip
    print_status "Upgrading pip..."
    python -m pip install --upgrade pip
    
    # Install requirements
    print_status "Installing chart requirements..."
    pip install -r chart_requirements.txt
    
    print_success "Chart requirements installed successfully with pip!"
}

# Function to install with conda
install_with_conda() {
    print_status "Installing requirements with conda..."
    
    # Check if conda is available
    if ! command_exists conda; then
        print_error "conda is not installed or not in PATH"
        print_status "Please install Anaconda or Miniconda first: https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    fi
    
    # Install requirements
    print_status "Installing chart requirements..."
    conda install -y pandas matplotlib seaborn numpy
    
    print_success "Chart requirements installed successfully with conda!"
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Test imports
    python -c "
import sys
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    print('✓ All required packages imported successfully')
    print(f'✓ pandas version: {pd.__version__}')
    print(f'✓ matplotlib version: {matplotlib.__version__}')
    print(f'✓ seaborn version: {sns.__version__}')
    print(f'✓ numpy version: {np.__version__}')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_success "Installation verification completed successfully!"
    else
        print_error "Installation verification failed!"
        exit 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [pip|conda]"
    echo ""
    echo "Options:"
    echo "  pip    Install using pip (default)"
    echo "  conda  Install using conda"
    echo ""
    echo "Examples:"
    echo "  $0        # Install with pip"
    echo "  $0 pip    # Install with pip"
    echo "  $0 conda  # Install with conda"
}

# Main script
main() {
    echo "🎯 Hailo AI People Counter - Chart Requirements Installer"
    echo "========================================================"
    echo ""
    
    # Parse command line arguments
    PACKAGE_MANAGER=${1:-pip}
    
    # Validate package manager
    if [ "$PACKAGE_MANAGER" != "pip" ] && [ "$PACKAGE_MANAGER" != "conda" ]; then
        print_error "Invalid package manager: $PACKAGE_MANAGER"
        show_usage
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "chart_requirements.txt" ]; then
        print_error "chart_requirements.txt not found in current directory"
        print_status "Please run this script from the Vision directory"
        exit 1
    fi
    
    # Check Python version
    print_status "Checking Python version..."
    if ! check_python_version python; then
        exit 1
    fi
    
    # Install requirements based on package manager
    case $PACKAGE_MANAGER in
        pip)
            install_with_pip
            ;;
        conda)
            install_with_conda
            ;;
    esac
    
    # Verify installation
    verify_installation
    
    echo ""
    print_success "Chart generator requirements installation completed!"
    print_status "You can now run: python generate_charts.py"
    echo ""
}

# Run main function with all arguments
main "$@" 