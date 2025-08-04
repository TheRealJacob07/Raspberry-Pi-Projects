"""
Hailo AI People Counter with CSV Logging
========================================

This program uses Hailo AI to detect and count people in real-time video streams.
It tracks unique individuals to avoid double counting and logs statistics to a CSV file.

Key Features:
- Real-time people detection using Hailo AI processor
- Unique individual tracking via track IDs
- Minute-by-minute CSV logging of people counts
- Visual display of statistics on video frames
- Thread-safe CSV operations with error handling

Author: Enhanced version of Hailo detection pipeline
Dependencies: Hailo AI, GStreamer, OpenCV, NumPy
"""

# Standard library imports for file operations, time tracking, and data handling
from pathlib import Path
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import numpy as np
import cv2
import hailo
import csv
import time
import threading
from datetime import datetime

# GStreamer imports for multimedia pipeline handling
import gi
gi.require_version('Gst', '1.0')  # Specify GStreamer version
from gi.repository import Gst, GLib  # GStreamer and GLib for multimedia processing

# Scientific computing and computer vision libraries
import numpy as np  # Numerical computing
import cv2  # Computer vision library for image processing

# Hailo AI framework for edge AI processing
import hailo

# Hailo-specific imports for buffer handling and pipeline management
from hailo_apps.hailo_app_python.core.common.buffer_utils import get_caps_from_pad, get_numpy_from_buffer
from hailo_apps.hailo_app_python.core.gstreamer.gstreamer_app import app_callback_class
from hailo_apps.hailo_app_python.apps.detection.detection_pipeline import GStreamerDetectionApp

# -----------------------------------------------------------------------------------------------
# User-defined class to be used in the callback function
# -----------------------------------------------------------------------------------------------
# Inheritance from the app_callback_class provides basic functionality for frame counting and data management
class user_app_callback_class(app_callback_class):
    """
    Custom callback class that extends the base Hailo callback functionality.
    This class manages people counting, tracking, and CSV logging operations.
    """
    
    def __init__(self):
        """Initialize the callback class with people counting and CSV logging capabilities."""
        # Call parent constructor to set up basic functionality
        super().__init__()
        
        # Example variable from original code (kept for compatibility)
        self.new_variable = 42  # New variable example

        # ===== PEOPLE COUNTING VARIABLES =====
        # Track the total number of unique people detected
        self.people_count = 0
        
        # Set to store unique track IDs to avoid counting the same person multiple times
        # Each person detected by Hailo gets a unique track ID that persists across frames
        self.tracked_people = set()
        
        # Timestamp of the last CSV log entry (used to determine when to log next)
        self.last_log_time = time.time()
        
        # CSV file name for storing people count data - use absolute path
        script_dir = Path(__file__).resolve().parent
        self.csv_file = script_dir / "people_count_log.csv"
        
        # Thread lock to prevent multiple threads from writing to CSV simultaneously
        # This ensures data integrity when the callback runs in a separate thread
        self.csv_lock = threading.Lock()
        
        # ===== ENHANCED TIME-BASED TRACKING =====
        # Track people detected in different time periods
        self.current_minute_people = set()
        self.current_hour_people = set()
        self.current_day_people = set()
        
        # Track the current time periods we're counting
        self.current_minute = int(time.time() // 60)
        self.current_hour = int(time.time() // 3600)
        self.current_day = int(time.time() // 86400)
        
        # ===== DEBUGGING VARIABLES =====
        # Last debug time for 10-second updates
        self.last_debug_time = time.time()
        
        # Initialize the CSV file with headers when the class is created
        self.init_csv_file()

    def new_function(self):
        """Example function from original code (kept for compatibility)."""
        return "The meaning of life is: "
    
    def init_csv_file(self):
        """
        Initialize CSV file with headers if it doesn't exist.
        Creates the CSV file with proper column headers for data logging.
        """
        try:
            # Try to create a new CSV file with headers
            # 'x' mode creates the file only if it doesn't exist
            with open(self.csv_file, 'x', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Write descriptive header comment
                writer.writerow(['# Hailo AI People Counter Data - Generated by Vision/main.py'])
                writer.writerow(['# This file contains people detection statistics for charting and analysis'])
                writer.writerow(['# Format: Timestamp, Minute, Hour, Day, People_This_Minute, People_This_Hour, People_This_Day, Total_Unique_People'])
                writer.writerow([])  # Empty row for separation
                # Write column headers for the CSV file with enhanced statistics
                writer.writerow(['Timestamp', 'Minute', 'Hour', 'Day', 'People_This_Minute', 'People_This_Hour', 'People_This_Day', 'Total_Unique_People'])
        except FileExistsError:
            # File already exists, don't overwrite (preserve existing data)
            # Check if file is empty and add headers if needed
            try:
                with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
                    content = file.read().strip()
                    if not content:
                        with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                            writer = csv.writer(file)
                            # Write descriptive header comment
                            writer.writerow(['# Hailo AI People Counter Data - Generated by Vision/main.py'])
                            writer.writerow(['# This file contains people detection statistics for charting and analysis'])
                            writer.writerow(['# Format: Timestamp, Minute, Hour, Day, People_This_Minute, People_This_Hour, People_This_Day, Total_Unique_People'])
                            writer.writerow([])  # Empty row for separation
                            writer.writerow(['Timestamp', 'Minute', 'Hour', 'Day', 'People_This_Minute', 'People_This_Hour', 'People_This_Day', 'Total_Unique_People'])
            except Exception:
                pass
        except Exception:
            pass
    
    def log_to_csv(self, people_count):
        """
        Log people count data to CSV file with timestamp and statistics.
        
        Args:
            people_count (int): Number of people detected in the current minute
        """
        # Get current timestamp for logging
        current_time = time.time()
        # Calculate current time periods since epoch
        minute = int(current_time // 60)
        hour = int(current_time // 3600)
        day = int(current_time // 86400)
        
        # Use thread lock to prevent multiple threads from writing simultaneously
        with self.csv_lock:
            try:
                # Open CSV file in append mode to add new data
                with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    # Format current timestamp for human readability
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # Prepare row data for CSV with enhanced statistics
                    row_data = [timestamp, minute, hour, day, len(self.current_minute_people), len(self.current_hour_people), len(self.current_day_people), len(self.tracked_people)]
                    # Write the data row to CSV
                    writer.writerow(row_data)
                    # Force flush to ensure data is written immediately
                    file.flush()
            except Exception as e:
                # Handle any errors during CSV writing
                print(f"Error writing to CSV: {e}")
        
        # Update the last log time to current time
        self.last_log_time = current_time
    
    def debug_status(self):
        """
        Print debug status every 10 seconds with current statistics.
        """
        current_time = time.time()
        if current_time - self.last_debug_time >= 10:  # Every 10 seconds
            print(f"\n=== DEBUG STATUS ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
            print(f"Current Minute People: {len(self.current_minute_people)}")
            print(f"Current Hour People: {len(self.current_hour_people)}")
            print(f"Current Day People: {len(self.current_day_people)}")
            print(f"Total Unique People: {len(self.tracked_people)}")
            print(f"Frame Count: {self.get_count()}")
            print(f"Time until next CSV log: {60 - (current_time - self.last_log_time):.1f} seconds")
            print("=" * 50)
            self.last_debug_time = current_time
    
    def add_person(self, track_id):
        """
        Add a person to the tracked set and increment count if they're new.
        Also tracks people detected in the current minute, hour, and day.
        
        Args:
            track_id (int): Unique track ID assigned by Hailo to this person
            
        Returns:
            bool: True if this is a new person, False if already tracked
        """
        # Check if this track ID has been seen before (lifetime tracking)
        is_new_person = False
        if track_id not in self.tracked_people:
            # Add to tracked set and increment total count
            self.tracked_people.add(track_id)
            self.people_count += 1
            is_new_person = True
        
        # Add to all current time period tracking
        self.current_minute_people.add(track_id)
        self.current_hour_people.add(track_id)
        self.current_day_people.add(track_id)
        
        return is_new_person  # Return whether this is a new person overall

# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------

# This is the callback function that will be called when data is available from the pipeline
def app_callback(pad, info, user_data):
    """
    Main callback function that processes each video frame and AI detection results.
    
    This function is called by the GStreamer pipeline for each frame that contains
    AI detection results from the Hailo processor.
    
    Args:
        pad: GStreamer pad that received the data
        info: GStreamer probe info containing the buffer
        user_data: Instance of user_app_callback_class for state management
        
    Returns:
        Gst.PadProbeReturn.OK: Indicates successful processing
    """
    
    # Get the GstBuffer from the probe info (contains video frame and AI results)
    buffer = info.get_buffer()
    
    # Check if the buffer is valid (safety check)
    if buffer is None:
        return Gst.PadProbeReturn.OK

    # ===== FRAME COUNTING =====
    # Increment the frame counter in user_data
    user_data.increment()
    # Note: Removed string_to_print initialization here as it's not used immediately

    # ===== VIDEO FRAME EXTRACTION =====
    # Get video format information from the GStreamer pad
    # This tells us the resolution and color format of the video
    format, width, height = get_caps_from_pad(pad)

    # Extract video frame data if frame processing is enabled
    frame = None
    if user_data.use_frame and format is not None and width is not None and height is not None:
        # Convert GStreamer buffer to NumPy array for OpenCV processing
        frame = get_numpy_from_buffer(buffer, format, width, height)

    # ===== AI DETECTION PROCESSING =====
    # Extract AI detection results from the Hailo buffer
    roi = hailo.get_roi_from_buffer(buffer)
    # Get all detected objects of type HAILO_DETECTION (people, cars, etc.)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # ===== PEOPLE COUNTING LOGIC =====
    # Count people detected in the current frame
    current_frame_people = 0
    string_to_print = ""
    # Process each detected object
    for detection in detections:
        # Extract detection information
        label = detection.get_label()  # Object class (e.g., "person", "car")
        bbox = detection.get_bbox()    # Bounding box coordinates
        confidence = detection.get_confidence()  # Detection confidence (0-1)
        
        # Only process person detections
        if label == "person":
            # ===== CONFIDENCE THRESHOLD CHECK =====
            # Only count people with 70% or higher confidence
            if confidence < 0.70:
                continue  # Skip this detection if confidence is too low
            
            # ===== TRACKING ID EXTRACTION =====
            # Get the unique track ID for this person
            # Track IDs persist across frames to identify the same person
            track_id = 0  # Default value
            track = detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
            if len(track) == 1:
                track_id = track[0].get_id()
            
            # ===== UNIQUE PERSON TRACKING =====
            # Add person to tracking system and check if they're new
            is_new_person = user_data.add_person(track_id)
            
            # Log detection information with different messages for new vs existing people
            if is_new_person:
                string_to_print = f"NEW PERSON DETECTED: ID: {track_id} Label: {label} Confidence: {confidence:.2f}\n"
                # Immediately log to CSV for testing when a new person is detected
                user_data.log_to_csv(len(user_data.current_minute_people)) # Log current minute people
            else:
                string_to_print = f"Detection: ID: {track_id} Label: {label} Confidence: {confidence:.2f}\n"
            
            # Increment current frame people count
            current_frame_people += 1
    
    # ===== CSV LOGGING LOGIC =====
    # Check if we've moved to a new time period and log the previous period's data
    # This ensures we count all people detected within each time period, not just the current frame
    current_time = time.time()
    current_minute = int(current_time // 60)
    current_hour = int(current_time // 3600)
    current_day = int(current_time // 86400)
    
    # Check if we've moved to a new minute
    if current_minute != user_data.current_minute:
        # We're in a new minute, log the previous minute's data
        people_in_last_minute = len(user_data.current_minute_people)
        user_data.log_to_csv(people_in_last_minute)
        string_to_print += f"Logged to CSV: {people_in_last_minute} people in the last minute, {len(user_data.tracked_people)} total unique people\n"
        
        # Reset current minute tracking for the new minute
        user_data.current_minute_people.clear()
        user_data.current_minute = current_minute
    
    # Check if we've moved to a new hour
    if current_hour != user_data.current_hour:
        # Reset current hour tracking for the new hour
        user_data.current_hour_people.clear()
        user_data.current_hour = current_hour
    
    # Check if we've moved to a new day
    if current_day != user_data.current_day:
        # Reset current day tracking for the new day
        user_data.current_day_people.clear()
        user_data.current_day = current_day
    
    # ===== DEBUG STATUS (every 10 seconds) =====
    user_data.debug_status()
    
    # ===== VIDEO FRAME ANNOTATION =====
    # Add visual information to the video frame if frame processing is enabled
    if user_data.use_frame:
        # Note: using imshow will not work here, as the callback function is not running in the main thread
        # Instead, we add text overlays to the frame for display
        
        # Display current frame people count on video
        cv2.putText(frame, f"Current Frame People: {current_frame_people}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display people detected in current minute on video
        cv2.putText(frame, f"Current Minute People: {len(user_data.current_minute_people)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display people detected in current hour on video
        cv2.putText(frame, f"Current Hour People: {len(user_data.current_hour_people)}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display people detected in current day on video
        cv2.putText(frame, f"Current Day People: {len(user_data.current_day_people)}", (10, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display total unique people count on video
        cv2.putText(frame, f"Total Unique People: {len(user_data.tracked_people)}", (10, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display example text from original code (kept for compatibility)
        cv2.putText(frame, f"{user_data.new_function()} {user_data.new_variable}", (10, 180), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Convert frame from RGB to BGR format (OpenCV uses BGR)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Store the processed frame for display by the main application
        user_data.set_frame(frame)

    # Print detection information to console for monitoring
    if string_to_print != "":
        print(string_to_print)
    
    # Return OK to indicate successful processing
    return Gst.PadProbeReturn.OK

# ===== MAIN PROGRAM ENTRY POINT =====
if __name__ == "__main__":
    """
    Main program entry point.
    Sets up the Hailo environment and starts the detection pipeline.
    """
    
    # ===== ENVIRONMENT SETUP =====
    # Get the project root directory (parent of current file)
    project_root = Path(__file__).resolve().parent.parent
    
    # Set up Hailo environment file path
    env_file = project_root / ".env"
    env_path_str = str(env_file)
    
    # Set environment variable for Hailo configuration
    os.environ["HAILO_ENV_FILE"] = env_path_str
    
    # ===== APPLICATION INITIALIZATION =====
    # Create an instance of our custom callback class
    # This object will manage all the people counting and CSV logging functionality
    user_data = user_app_callback_class()
    
    # Create the GStreamer detection application
    # This sets up the video pipeline, Hailo AI processing, and connects our callback
    app = GStreamerDetectionApp(app_callback, user_data)
    
    # ===== START THE APPLICATION =====
    # Run the detection pipeline
    # This will start video capture, AI processing, and call our callback for each frame
    app.run()
