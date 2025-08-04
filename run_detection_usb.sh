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
if [ ! -f "Resources/hailo-rpi5-examples-main/basic_pipelines/detection.py" ]; then
    echo "Error: detection.py not found at Resources/hailo-rpi5-examples-main/basic_pipelines/detection.py"
    exit 1
fi

# Run the detection script with USB input
python Resources/hailo-rpi5-examples-main/basic_pipelines/detection.py --input usb

# Check if the script ran successfully
if [ $? -eq 0 ]; then
    echo "Detection script completed successfully"
else
    echo "Detection script failed with exit code $?"
fi 