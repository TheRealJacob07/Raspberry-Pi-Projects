"""
People Counter Web Dashboard
===========================

Flask web application that displays people count data with interactive graphs
and a timelapse from the USB camera.

Features:
- Real-time people count display
- Interactive charts using Chart.js
- Timelapse from USB camera
- Responsive design
"""

from flask import Flask, render_template, jsonify, request, Response
import requests
import json
import cv2
import threading
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
import base64
import numpy as np

app = Flask(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"
CAMERA_INDEX = 0  # USB camera index
TIMELAPSE_INTERVAL = 2  # seconds between captures
TIMELAPSE_DURATION = 600  # 10 minutes in seconds
FRAMES_DIR = Path("web_dashboard/static/frames")

# Ensure frames directory exists
FRAMES_DIR.mkdir(parents=True, exist_ok=True)

# Global variables for camera and timelapse
camera = None
camera_lock = threading.Lock()
timelapse_frames = []
timelapse_running = False

def init_camera():
    """Initialize USB camera."""
    global camera
    try:
        camera = cv2.VideoCapture(CAMERA_INDEX)
        if not camera.isOpened():
            print(f"Error: Could not open camera at index {CAMERA_INDEX}")
            return False
        
        # Set camera properties
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 30)
        
        print("Camera initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return False

def capture_frame():
    """Capture a single frame from the camera."""
    global camera
    if camera is None:
        return None
    
    with camera_lock:
        ret, frame = camera.read()
        if ret:
            # Resize frame for web display
            frame = cv2.resize(frame, (320, 240))
            return frame
        return None

def timelapse_worker():
    """Background worker for capturing timelapse frames."""
    global timelapse_frames, timelapse_running
    
    while timelapse_running:
        frame = capture_frame()
        if frame is not None:
            # Convert frame to base64 for web display
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_b64 = base64.b64encode(buffer).decode('utf-8')
            
            timestamp = datetime.now().isoformat()
            timelapse_frames.append({
                'timestamp': timestamp,
                'frame': frame_b64
            })
            
            # Keep only the last 10 minutes of frames (300 frames at 2-second intervals)
            if len(timelapse_frames) > 300:
                timelapse_frames.pop(0)
        
        time.sleep(TIMELAPSE_INTERVAL)

def start_timelapse():
    """Start the timelapse capture."""
    global timelapse_running
    if not timelapse_running:
        timelapse_running = True
        threading.Thread(target=timelapse_worker, daemon=True).start()

def stop_timelapse():
    """Stop the timelapse capture."""
    global timelapse_running
    timelapse_running = False

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/people-data')
def get_people_data():
    """Get people count data from the API."""
    try:
        # Get current data
        current_response = requests.get(f"{API_BASE_URL}/data/current", timeout=5)
        current_data = current_response.json() if current_response.status_code == 200 else {}
        
        # Get hourly data
        hourly_response = requests.get(f"{API_BASE_URL}/data/hourly?hours=24", timeout=5)
        hourly_data = hourly_response.json() if hourly_response.status_code == 200 else {}
        
        # Get summary data
        summary_response = requests.get(f"{API_BASE_URL}/data/summary", timeout=5)
        summary_data = summary_response.json() if summary_response.status_code == 200 else {}
        
        return jsonify({
            'current': current_data.get('current_data', {}),
            'hourly': hourly_data.get('hourly_data', []),
            'summary': summary_data.get('summary', {}),
            'timestamp': datetime.now().isoformat()
        })
    except requests.RequestException as e:
        return jsonify({'error': f'API connection error: {str(e)}'}), 500

@app.route('/api/timelapse')
def get_timelapse():
    """Get timelapse frames."""
    global timelapse_frames
    return jsonify({
        'frames': timelapse_frames,
        'count': len(timelapse_frames),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/timelapse/start')
def start_timelapse_api():
    """Start timelapse capture."""
    start_timelapse()
    return jsonify({'status': 'started', 'message': 'Timelapse started'})

@app.route('/api/timelapse/stop')
def stop_timelapse_api():
    """Stop timelapse capture."""
    stop_timelapse()
    return jsonify({'status': 'stopped', 'message': 'Timelapse stopped'})

@app.route('/api/camera/status')
def camera_status():
    """Get camera status."""
    global camera
    if camera is None:
        return jsonify({'status': 'not_initialized'})
    
    is_opened = camera.isOpened()
    return jsonify({
        'status': 'connected' if is_opened else 'disconnected',
        'opened': is_opened
    })

@app.route('/api/camera/frame')
def get_camera_frame():
    """Get current camera frame."""
    frame = capture_frame()
    if frame is not None:
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        frame_b64 = base64.b64encode(buffer).decode('utf-8')
        return jsonify({
            'frame': frame_b64,
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({'error': 'No frame available'}), 404

if __name__ == '__main__':
    print("Starting People Counter Web Dashboard...")
    
    # Initialize camera
    if init_camera():
        print("Camera initialized successfully")
        # Start timelapse automatically
        start_timelapse()
    else:
        print("Warning: Camera initialization failed")
    
    print("Dashboard will be available at: http://localhost:5000")
    print("Make sure the API is running at: http://localhost:8000")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        # Cleanup
        stop_timelapse()
        if camera is not None:
            camera.release() 