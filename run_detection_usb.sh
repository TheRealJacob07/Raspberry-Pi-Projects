#!/bin/bash

# Hailo AI Detection Script - USB Input
# This script runs the Hailo detection pipeline with USB camera input

echo "Starting Hailo AI Detection with USB camera..."
echo

# Change to the script's directory
cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# Check if the detection script exists
if [ ! -f "People-Counter/main.py" ]; then
    echo "Error: detection.py not found at People-Counter/main.py"
    exit 1
fi

echo "Running detection script..."
gnome-terminal -- python People-Counter/main.py --input usb

# Check if the script ran successfully
if [ $? -eq 0 ]; then
    echo "Detection script completed successfully"
else
    echo "Detection script failed with exit code $?"
fi 
