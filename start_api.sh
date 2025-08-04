#!/bin/bash

# Hailo AI People Counter API Startup Script
# ==========================================
# This script provides an easy way to start, stop, and manage the API server

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$SCRIPT_DIR/API"
API_FILE="$API_DIR/api.py"
REQUIREMENTS_FILE="$API_DIR/api_requirements.txt"
CSV_FILE="$SCRIPT_DIR/People-Counter/people_count_log.csv"
PID_FILE="$API_DIR/api.pid"
LOG_FILE="$API_DIR/api.log"
PORT=8000
HOST="0.0.0.0"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Hailo AI People Counter API${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if Python is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        if ! command -v python &> /dev/null; then
            print_error "Python is not installed or not in PATH"
            print_error "Please install Python 3.7+ and try again"
            exit 1
        else
            PYTHON_CMD="python"
        fi
    else
        PYTHON_CMD="python3"
    fi
    
    print_status "Using Python: $($PYTHON_CMD --version)"
}

# Function to check if required files exist
check_files() {
    if [ ! -d "$API_DIR" ]; then
        print_error "API directory not found: $API_DIR"
        exit 1
    fi
    
    if [ ! -f "$API_FILE" ]; then
        print_error "API file not found: $API_FILE"
        exit 1
    fi
    
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        print_error "Requirements file not found: $REQUIREMENTS_FILE"
        exit 1
    fi
    
    if [ ! -f "$CSV_FILE" ]; then
        print_warning "CSV file not found: $CSV_FILE"
        print_warning "API will start but may return no data"
        print_warning "Run the people counter first to generate data"
    else
        print_status "CSV file found: $CSV_FILE"
        # Check file permissions
        if [ ! -r "$CSV_FILE" ]; then
            print_warning "CSV file is not readable: $CSV_FILE"
            print_warning "You may need to adjust file permissions"
            print_warning "Try: chmod 644 $CSV_FILE"
        else
            print_status "CSV file is readable"
        fi
    fi
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    if ! $PYTHON_CMD -m pip install -r "$REQUIREMENTS_FILE" --break-system-packages; then
        print_error "Failed to install dependencies"
        print_error "Please check your internet connection and try again"
        exit 1
    fi
    
    print_status "Dependencies installed successfully"
}

# Function to check if API is already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            print_warning "API is already running (PID: $PID)"
            return 0
        else
            print_warning "Stale PID file found, removing..."
            rm -f "$PID_FILE"
        fi
    fi
    return 1
}

# Function to start the API
start_api() {
    print_header
    
    check_python
    check_files
    
    if check_running; then
        print_warning "API is already running"
        print_status "Use './start_api.sh stop' to stop the API"
        print_status "Use './start_api.sh restart' to restart the API"
        return 0
    fi
    
    # Change to API directory for installation
    cd "$API_DIR"
    install_dependencies
    cd "$SCRIPT_DIR"
    
    print_status "Starting API server on $HOST:$PORT"
    print_status "Log file: $LOG_FILE"
    print_status "Press Ctrl+C to stop the server"
    
    # Start the API in the background
    cd "$API_DIR"
    nohup $PYTHON_CMD "$API_FILE" > "$LOG_FILE" 2>&1 &
    API_PID=$!
    cd "$SCRIPT_DIR"
    
    # Save PID to file
    echo $API_PID > "$PID_FILE"
    
    # Wait a moment to check if it started successfully
    sleep 2
    
    if ps -p "$API_PID" > /dev/null 2>&1; then
        print_status "API started successfully (PID: $API_PID)"
        print_status "API is available at: http://localhost:$PORT"
        print_status "To view logs: tail -f $LOG_FILE"
        print_status "To stop API: ./start_api.sh stop"
    else
        print_error "Failed to start API"
        print_error "Check the log file: $LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Function to stop the API
stop_api() {
    print_status "Stopping API server..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            print_status "Stopping process $PID..."
            kill "$PID"
            
            # Wait for process to stop
            for i in {1..10}; do
                if ! ps -p "$PID" > /dev/null 2>&1; then
                    print_status "API stopped successfully"
                    rm -f "$PID_FILE"
                    return 0
                fi
                sleep 1
            done
            
            print_warning "API did not stop gracefully, forcing termination..."
            kill -9 "$PID" 2>/dev/null
            rm -f "$PID_FILE"
            print_status "API forced to stop"
        else
            print_warning "API is not running"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "No PID file found, API may not be running"
    fi
}

# Function to restart the API
restart_api() {
    print_status "Restarting API server..."
    stop_api
    sleep 2
    start_api
}

# Function to show API status
show_status() {
    print_header
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            print_status "API is running (PID: $PID)"
            print_status "API URL: http://localhost:$PORT"
            
            # Check if API is responding
            if command -v curl &> /dev/null; then
                if curl -s "http://localhost:$PORT/" > /dev/null 2>&1; then
                    print_status "API is responding to requests"
                else
                    print_warning "API is running but not responding to requests"
                fi
            fi
            
            print_status "Log file: $LOG_FILE"
            print_status "Recent log entries:"
            tail -n 5 "$LOG_FILE" 2>/dev/null || print_warning "No log file found"
        else
            print_warning "API is not running (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "API is not running"
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_status "Showing API logs (press Ctrl+C to exit):"
        tail -f "$LOG_FILE"
    else
        print_warning "No log file found"
    fi
}

# Function to test the API
test_api() {
    print_status "Testing API endpoints..."
    
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed. Please install curl to test the API."
        return 1
    fi
    
    BASE_URL="http://localhost:$PORT"
    
    # Test API info endpoint
    print_status "Testing API info endpoint..."
    if curl -s "$BASE_URL/" | grep -q "api_name"; then
        print_status "✓ API info endpoint working"
    else
        print_error "✗ API info endpoint failed"
        return 1
    fi
    
    # Test latest data endpoint
    print_status "Testing latest data endpoint..."
    if curl -s "$BASE_URL/data/latest" | grep -q "latest_data"; then
        print_status "✓ Latest data endpoint working"
    else
        print_warning "⚠ Latest data endpoint returned no data (this is normal if no CSV data exists)"
    fi
    
    # Test summary endpoint
    print_status "Testing summary endpoint..."
    if curl -s "$BASE_URL/data/summary" | grep -q "summary"; then
        print_status "✓ Summary endpoint working"
    else
        print_warning "⚠ Summary endpoint returned no data (this is normal if no CSV data exists)"
    fi
    
    print_status "API test completed"
}

# Function to show help
show_help() {
    print_header
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the API server (default)"
    echo "  stop      Stop the API server"
    echo "  restart   Restart the API server"
    echo "  status    Show API server status"
    echo "  logs      Show API server logs"
    echo "  test      Test API endpoints"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Start the API server"
    echo "  $0 start        # Start the API server"
    echo "  $0 stop         # Stop the API server"
    echo "  $0 status       # Check if API is running"
    echo "  $0 test         # Test API endpoints"
    echo ""
    echo "Configuration:"
    echo "  Port: $PORT"
    echo "  Host: $HOST"
    echo "  API Directory: $API_DIR"
    echo "  CSV File: $CSV_FILE"
    echo "  Log file: $LOG_FILE"
    echo "  PID file: $PID_FILE"
    echo ""
    echo "Note: Make sure to run the people counter first to generate CSV data"
}

# Main script logic
case "${1:-start}" in
    start)
        start_api
        ;;
    stop)
        stop_api
        ;;
    restart)
        restart_api
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    test)
        test_api
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 