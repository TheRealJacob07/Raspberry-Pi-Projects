#!/bin/bash

# People Counter Web Dashboard Startup Script
# This script starts the web dashboard with proper setup

echo "Starting People Counter Web Dashboard..."
echo

# Change to the script's directory
cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# Check if the web dashboard directory exists
if [ ! -d "web_dashboard" ]; then
    echo "Error: web_dashboard directory not found"
    exit 1
fi

# Check if the API is running
echo "Checking if API is running..."
if curl -s http://localhost:8000 > /dev/null; then
    echo "✓ API is running on http://localhost:8000"
else
    echo "⚠ Warning: API is not running on http://localhost:8000"
    echo "  Please start the API first with: python API/api.py"
    echo "  Or run: ./start_api.sh"
    echo
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install dependencies if needed
echo "Checking dependencies..."
if [ ! -f "web_dashboard/venv/bin/activate" ]; then
    echo "Creating virtual environment..."
    python -m venv web_dashboard/venv
fi

# Activate virtual environment
source web_dashboard/venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r web_dashboard/requirements.txt

# Check if camera is available
echo "Checking camera availability..."
python -c "
import cv2
camera = cv2.VideoCapture(0)
if camera.isOpened():
    print('✓ USB camera is available')
    camera.release()
else:
    print('⚠ Warning: USB camera not available')
    print('  The timelapse feature will not work')
"

echo
echo "Starting web dashboard..."
echo "Dashboard will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo

# Start the web dashboard
cd web_dashboard
python app.py 