# People Counter Web Dashboard

A modern, responsive web dashboard for monitoring people count data with interactive charts and USB camera timelapse functionality.

## Features

- **Real-time Statistics**: Live display of people count for current minute, hour, day, and total unique people
- **Interactive Charts**: Beautiful charts showing hourly traffic patterns and summary statistics
- **USB Camera Timelapse**: 10-minute timelapse from USB camera with frame-by-frame playback
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **API Integration**: Connects to the People Counter API for real-time data
- **Modern UI**: Clean, modern interface with smooth animations and hover effects

## Screenshots

The dashboard includes:
- Statistics cards with real-time data
- Line chart showing hourly people traffic
- Doughnut chart with traffic summary
- Timelapse viewer with camera controls

## Prerequisites

1. **Python 3.7+** installed on your system
2. **People Counter API** running on `http://localhost:8000`
3. **USB Camera** connected (for timelapse feature)
4. **OpenCV** support for camera access

## Installation

### Option 1: Using the startup script (Recommended)

```bash
# Make the script executable
chmod +x start_web_dashboard.sh

# Run the startup script
./start_web_dashboard.sh
```

The startup script will:
- Check if Python is installed
- Verify the API is running
- Create a virtual environment
- Install dependencies
- Check camera availability
- Start the web dashboard

### Option 2: Manual installation

```bash
# Navigate to the web dashboard directory
cd web_dashboard

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the dashboard
python app.py
```

## Usage

1. **Start the API first**:
   ```bash
   python API/api.py
   # Or use the startup script
   ./start_api.sh
   ```

2. **Start the web dashboard**:
   ```bash
   ./start_web_dashboard.sh
   ```

3. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Dashboard Features

### Statistics Cards
- **This Minute**: Number of people detected in the current minute
- **This Hour**: Number of people detected in the current hour
- **This Day**: Number of people detected in the current day
- **Total Unique**: Total number of unique people detected

### Charts
- **Hourly Traffic**: Line chart showing people count per hour over the last 24 hours
- **Traffic Summary**: Doughnut chart showing distribution of current traffic

### Timelapse
- **Live Capture**: Automatically captures frames every 2 seconds
- **10-minute History**: Stores the last 10 minutes of frames
- **Controls**: Start/stop timelapse capture
- **Frame Display**: Shows timestamps for each frame

## API Endpoints

The dashboard uses the following API endpoints:

- `GET /api/people-data` - Fetches current, hourly, and summary data
- `GET /api/timelapse` - Gets timelapse frames
- `GET /api/timelapse/start` - Starts timelapse capture
- `GET /api/timelapse/stop` - Stops timelapse capture
- `GET /api/camera/status` - Gets camera connection status
- `GET /api/camera/frame` - Gets current camera frame

## Configuration

You can modify the configuration in `app.py`:

```python
# API configuration
API_BASE_URL = "http://localhost:8000"

# Camera configuration
CAMERA_INDEX = 0  # USB camera index
TIMELAPSE_INTERVAL = 2  # seconds between captures
TIMELAPSE_DURATION = 600  # 10 minutes in seconds

# Web server configuration
PORT = 5000
```

## Troubleshooting

### API Connection Issues
- Ensure the People Counter API is running on port 8000
- Check if the API is accessible: `curl http://localhost:8000`
- Verify the CSV file exists and is readable

### Camera Issues
- Check if USB camera is connected and recognized
- Try different camera indices (0, 1, 2, etc.)
- Ensure OpenCV is properly installed
- Check camera permissions on Linux systems

### Performance Issues
- Reduce timelapse interval for better performance
- Lower image quality in camera settings
- Close other applications using the camera

### Browser Issues
- Clear browser cache if charts don't load
- Ensure JavaScript is enabled
- Try a different browser if issues persist

## Development

### Project Structure
```
web_dashboard/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── templates/
│   └── dashboard.html # Main dashboard template
└── static/
    └── frames/        # Timelapse frame storage
```

### Adding New Features
1. Modify `app.py` to add new API endpoints
2. Update `templates/dashboard.html` for UI changes
3. Add new JavaScript functions for interactivity
4. Update `requirements.txt` if new dependencies are needed

## Dependencies

- **Flask**: Web framework
- **requests**: HTTP client for API calls
- **opencv-python**: Camera access and image processing
- **numpy**: Numerical computing
- **Pillow**: Image processing

## License

This project is part of the Hailo AI People Counter system.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Check the API logs for errors
4. Ensure camera permissions are correct 