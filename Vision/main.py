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
        
        # CSV file name for storing people count data
        self.csv_file = "people_count_log.csv"
        
        # Thread lock to prevent multiple threads from writing to CSV simultaneously
        # This ensures data integrity when the callback runs in a separate thread
        self.csv_lock = threading.Lock()
        
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
        print(f"DEBUG: Initializing CSV file: {self.csv_file}")
        try:
            # Try to create a new CSV file with headers
            # 'x' mode creates the file only if it doesn't exist
            with open(self.csv_file, 'x', newline='') as file:
                writer = csv.writer(file)
                # Write column headers for the CSV file
                writer.writerow(['Timestamp', 'Minute', 'People_Count', 'Total_Unique_People'])
                print(f"DEBUG: Created new CSV file with headers: {self.csv_file}")
        except FileExistsError:
            # File already exists, don't overwrite (preserve existing data)
            print(f"DEBUG: CSV file already exists: {self.csv_file}")
        except Exception as e:
            # Handle any other errors during file creation
            print(f"DEBUG: Error creating CSV file: {e}")
            print(f"DEBUG: Current working directory: {os.getcwd()}")
            print(f"DEBUG: Absolute path: {os.path.abspath(self.csv_file)}")
    
    def log_to_csv(self, people_count):
        """
        Log people count data to CSV file with timestamp and statistics.
        
        Args:
            people_count (int): Number of people detected in the current minute
        """
        # Get current timestamp for logging
        current_time = time.time()
        # Calculate current minute since epoch (used for grouping data)
        minute = int(current_time // 60)
        
        print(f"DEBUG: Attempting to write to CSV file: {self.csv_file}")
        print(f"DEBUG: Data to write - People count: {people_count}, Total unique: {len(self.tracked_people)}")
        
        # Use thread lock to prevent multiple threads from writing simultaneously
        with self.csv_lock:
            try:
                # Open CSV file in append mode to add new data
                with open(self.csv_file, 'a', newline='') as file:
                    writer = csv.writer(file)
                    # Format current timestamp for human readability
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # Prepare row data for CSV
                    row_data = [timestamp, minute, people_count, len(self.tracked_people)]
                    # Write the data row to CSV
                    writer.writerow(row_data)
                    print(f"DEBUG: Successfully wrote row to CSV: {row_data}")
            except Exception as e:
                # Handle any errors during CSV writing
                print(f"Error writing to CSV: {e}")
                print(f"DEBUG: CSV file path: {os.path.abspath(self.csv_file)}")
        
        # Update the last log time to current time
        self.last_log_time = current_time
    
    def add_person(self, track_id):
        """
        Add a person to the tracked set and increment count if they're new.
        
        Args:
            track_id (int): Unique track ID assigned by Hailo to this person
            
        Returns:
            bool: True if this is a new person, False if already tracked
        """
        # Check if this track ID has been seen before
        if track_id not in self.tracked_people:
            # Add to tracked set and increment total count
            self.tracked_people.add(track_id)
            self.people_count += 1
            return True  # This is a new person
        return False  # Person already tracked

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
    
    # Process each detected object
    for detection in detections:
        # Extract detection information
        label = detection.get_label()  # Object class (e.g., "person", "car")
        bbox = detection.get_bbox()    # Bounding box coordinates
        confidence = detection.get_confidence()  # Detection confidence (0-1)
        
        # Only process person detections
        if label == "person":
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
            else:
                string_to_print = f"Detection: ID: {track_id} Label: {label} Confidence: {confidence:.2f}\n"
            
            # Increment current frame people count
            current_frame_people += 1
    
    # ===== CSV LOGGING LOGIC =====
    # Check if it's time to log data to CSV (every 60 seconds)
    current_time = time.time()
    if current_time - user_data.last_log_time >= 60:  # 60 seconds = 1 minute
        # Log current people count to CSV file
        user_data.log_to_csv(current_frame_people)
        string_to_print += f"Logged to CSV: {current_frame_people} people in this minute, {len(user_data.tracked_people)} total unique people\n"
        print(f"DEBUG: CSV logging triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        # Debug: show time until next log (only print every 120 frames to avoid spam)
        time_until_log = 60 - (current_time - user_data.last_log_time)
        if user_data.get_count() % 120 == 0:  # Print every 120 frames to avoid spam
            print(f"DEBUG: {time_until_log:.1f} seconds until next CSV log")
    
    # ===== VIDEO FRAME ANNOTATION =====
    # Add visual information to the video frame if frame processing is enabled
    if user_data.use_frame:
        # Note: using imshow will not work here, as the callback function is not running in the main thread
        # Instead, we add text overlays to the frame for display
        
        # Display current frame people count on video
        cv2.putText(frame, f"Current Frame People: {current_frame_people}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display total unique people count on video
        cv2.putText(frame, f"Total Unique People: {len(user_data.tracked_people)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display example text from original code (kept for compatibility)
        cv2.putText(frame, f"{user_data.new_function()} {user_data.new_variable}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Convert frame from RGB to BGR format (OpenCV uses BGR)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Store the processed frame for display by the main application
        user_data.set_frame(frame)

    # Print detection information to console for monitoring
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
