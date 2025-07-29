#!/bin/bash

# Hailo AI People Counter - Web Dashboard Requirements Installer (Linux)
# =====================================================================
#
# This script installs the required Python packages for the web dashboard.
# It supports both pip and conda environments on Linux systems.
#
# Usage: ./install_web_requirements.sh [pip|conda]
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

# Function to install system dependencies
install_system_dependencies() {
    print_status "Installing system dependencies..."
    
    # Detect Linux distribution
    if command_exists apt-get; then
        # Debian/Ubuntu
        print_status "Detected Debian/Ubuntu system"
        sudo apt-get update
        sudo apt-get install -y python3-pip python3-venv build-essential python3-dev
    elif command_exists yum; then
        # CentOS/RHEL/Fedora
        print_status "Detected CentOS/RHEL/Fedora system"
        sudo yum install -y python3-pip python3-devel gcc
    elif command_exists dnf; then
        # Fedora (newer versions)
        print_status "Detected Fedora system"
        sudo dnf install -y python3-pip python3-devel gcc
    elif command_exists pacman; then
        # Arch Linux
        print_status "Detected Arch Linux system"
        sudo pacman -S --noconfirm python-pip base-devel
    elif command_exists zypper; then
        # openSUSE
        print_status "Detected openSUSE system"
        sudo zypper install -y python3-pip python3-devel gcc
    else
        print_warning "Could not detect package manager. Please install Python 3.7+ and pip manually."
        return 1
    fi
    
    print_success "System dependencies installed"
}

# Function to install with pip
install_with_pip() {
    print_status "Installing web dashboard requirements with pip..."
    
    # Check if pip is available
    if ! command_exists pip; then
        print_error "pip is not installed or not in PATH"
        print_status "Attempting to install pip..."
        install_system_dependencies
    fi
    
    # Upgrade pip
    print_status "Upgrading pip..."
    python3 -m pip install --upgrade pip
    
    # Install requirements
    print_status "Installing web dashboard requirements..."
    pip install -r web_requirements.txt
    
    print_success "Web dashboard requirements installed successfully with pip!"
}

# Function to install with conda
install_with_conda() {
    print_status "Installing web dashboard requirements with conda..."
    
    # Check if conda is available
    if ! command_exists conda; then
        print_error "conda is not installed or not in PATH"
        print_status "Please install Anaconda or Miniconda first: https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    fi
    
    # Install requirements
    print_status "Installing web dashboard requirements..."
    conda install -y flask pandas plotly numpy
    
    print_success "Web dashboard requirements installed successfully with conda!"
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Test imports
    python3 -c "
import sys
try:
    import flask
    import pandas as pd
    import plotly.graph_objs as go
    import numpy as np
    print('✓ All required packages imported successfully')
    print(f'✓ Flask version: {flask.__version__}')
    print(f'✓ pandas version: {pd.__version__}')
    print(f'✓ plotly version: {plotly.__version__}')
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

# Function to create virtual environment
create_virtual_env() {
    print_status "Creating virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment 'venv' already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
        else
            print_status "Using existing virtual environment"
            return 0
        fi
    fi
    
    python3 -m venv venv
    print_success "Virtual environment created: venv/"
    
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    print_status "Installing requirements in virtual environment..."
    pip install -r web_requirements.txt
    
    print_success "Virtual environment setup completed!"
    print_status "To activate: source venv/bin/activate"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [pip|conda] [--venv]"
    echo ""
    echo "Options:"
    echo "  pip      Install using pip (default)"
    echo "  conda    Install using conda"
    echo "  --venv   Create and use virtual environment"
    echo ""
    echo "Examples:"
    echo "  $0              # Install with pip"
    echo "  $0 pip          # Install with pip"
    echo "  $0 conda        # Install with conda"
    echo "  $0 --venv       # Create virtual environment and install"
    echo "  $0 pip --venv   # Install with pip in virtual environment"
}

# Function to check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_warning "Running as root. This is not recommended for security reasons."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Main script
main() {
    echo "🌐 Hailo AI People Counter - Web Dashboard Requirements Installer"
    echo "================================================================="
    echo ""
    
    # Check if running as root
    check_root
    
    # Parse command line arguments
    PACKAGE_MANAGER="pip"
    USE_VENV=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            pip|conda)
                PACKAGE_MANAGER="$1"
                shift
                ;;
            --venv)
                USE_VENV=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Check if we're in the right directory
    if [ ! -f "web_requirements.txt" ]; then
        print_error "web_requirements.txt not found in current directory"
        print_status "Please run this script from the Vision directory"
        exit 1
    fi
    
    # Check Python version
    print_status "Checking Python version..."
    if ! check_python_version python3; then
        exit 1
    fi
    
    # Handle virtual environment
    if [ "$USE_VENV" = true ]; then
        create_virtual_env
        verify_installation
    else
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
    fi
    
    echo ""
    print_success "Web dashboard requirements installation completed!"
    print_status "You can now run: python3 start_dashboard.py"
    print_status "Or: python3 web_dashboard.py"
    echo ""
    
    if [ "$USE_VENV" = true ]; then
        print_status "Remember to activate the virtual environment:"
        print_status "  source venv/bin/activate"
        echo ""
    fi
}

# Run main function with all arguments
main "$@" 