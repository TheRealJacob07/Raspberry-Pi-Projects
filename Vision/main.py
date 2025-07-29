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

from hailo_apps.hailo_app_python.core.common.buffer_utils import get_caps_from_pad, get_numpy_from_buffer
from hailo_apps.hailo_app_python.core.gstreamer.gstreamer_app import app_callback_class
from hailo_apps.hailo_app_python.apps.detection.detection_pipeline import GStreamerDetectionApp

# -----------------------------------------------------------------------------------------------
# User-defined class to be used in the callback function
# -----------------------------------------------------------------------------------------------
# Inheritance from the app_callback_class
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.new_variable = 42  # New variable example
        
        # People counting variables
        self.people_count = 0
        self.tracked_people = set()  # Set to track unique people by track ID
        self.last_log_time = time.time()
        self.csv_file = "people_count_log.csv"
        self.csv_lock = threading.Lock()  # Thread lock for CSV operations
        
        # Initialize CSV file with headers
        self.init_csv_file()

    def new_function(self):  # New function example
        return "The meaning of life is: "
    
    def init_csv_file(self):
        """Initialize CSV file with headers if it doesn't exist"""
        print(f"DEBUG: Initializing CSV file: {self.csv_file}")
        try:
            with open(self.csv_file, 'x', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Timestamp', 'Minute', 'People_Count', 'Total_Unique_People'])
                print(f"DEBUG: Created new CSV file with headers: {self.csv_file}")
        except FileExistsError:
            # File already exists, don't overwrite
            print(f"DEBUG: CSV file already exists: {self.csv_file}")
        except Exception as e:
            print(f"DEBUG: Error creating CSV file: {e}")
            print(f"DEBUG: Current working directory: {os.getcwd()}")
            print(f"DEBUG: Absolute path: {os.path.abspath(self.csv_file)}")
    
    def log_to_csv(self, people_count):
        """Log people count to CSV file"""
        current_time = time.time()
        minute = int(current_time // 60)  # Current minute since epoch
        
        print(f"DEBUG: Attempting to write to CSV file: {self.csv_file}")
        print(f"DEBUG: Data to write - People count: {people_count}, Total unique: {len(self.tracked_people)}")
        
        with self.csv_lock:
            try:
                with open(self.csv_file, 'a', newline='') as file:
                    writer = csv.writer(file)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    row_data = [timestamp, minute, people_count, len(self.tracked_people)]
                    writer.writerow(row_data)
                    print(f"DEBUG: Successfully wrote row to CSV: {row_data}")
            except Exception as e:
                print(f"Error writing to CSV: {e}")
                print(f"DEBUG: CSV file path: {os.path.abspath(self.csv_file)}")
        
        self.last_log_time = current_time
    
    def add_person(self, track_id):
        """Add a person to the tracked set and increment count if new"""
        if track_id not in self.tracked_people:
            self.tracked_people.add(track_id)
            self.people_count += 1
            return True
        return False

# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------

# This is the callback function that will be called when data is available from the pipeline
def app_callback(pad, info, user_data):
    # Get the GstBuffer from the probe info
    buffer = info.get_buffer()
    # Check if the buffer is valid
    if buffer is None:
        return Gst.PadProbeReturn.OK

    # Using the user_data to count the number of frames
    user_data.increment()
    string_to_print = f"Frame count: {user_data.get_count()}\n"

    # Get the caps from the pad
    format, width, height = get_caps_from_pad(pad)

    # If the user_data.use_frame is set to True, we can get the video frame from the buffer
    frame = None
    if user_data.use_frame and format is not None and width is not None and height is not None:
        # Get video frame
        frame = get_numpy_from_buffer(buffer, format, width, height)

    # Get the detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # Parse the detections and count people
    current_frame_people = 0
    for detection in detections:
        label = detection.get_label()
        bbox = detection.get_bbox()
        confidence = detection.get_confidence()
        if label == "person":
            # Get track ID
            track_id = 0
            track = detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
            if len(track) == 1:
                track_id = track[0].get_id()
            
            # Add person to tracking if new
            is_new_person = user_data.add_person(track_id)
            if is_new_person:
                string_to_print += f"NEW PERSON DETECTED: ID: {track_id} Label: {label} Confidence: {confidence:.2f}\n"
            else:
                string_to_print += f"Detection: ID: {track_id} Label: {label} Confidence: {confidence:.2f}\n"
            current_frame_people += 1
    
    # Check if it's time to log to CSV (every minute)
    current_time = time.time()
    if current_time - user_data.last_log_time >= 60:  # 60 seconds = 1 minute
        user_data.log_to_csv(current_frame_people)
        string_to_print += f"Logged to CSV: {current_frame_people} people in this minute, {len(user_data.tracked_people)} total unique people\n"
        print(f"DEBUG: CSV logging triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        # Debug: show time until next log
        time_until_log = 60 - (current_time - user_data.last_log_time)
        if user_data.get_count() % 30 == 0:  # Print every 30 frames to avoid spam
            print(f"DEBUG: {time_until_log:.1f} seconds until next CSV log")
    
    if user_data.use_frame:
        # Note: using imshow will not work here, as the callback function is not running in the main thread
        # Let's print the detection count to the frame
        cv2.putText(frame, f"Current Frame People: {current_frame_people}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Total Unique People: {len(user_data.tracked_people)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # Example of how to use the new_variable and new_function from the user_data
        # Let's print the new_variable and the result of the new_function to the frame
        cv2.putText(frame, f"{user_data.new_function()} {user_data.new_variable}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # Convert the frame to BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        user_data.set_frame(frame)

    print(string_to_print)
    return Gst.PadProbeReturn.OK

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    env_file     = project_root / ".env"
    env_path_str = str(env_file)
    os.environ["HAILO_ENV_FILE"] = env_path_str
    # Create an instance of the user app callback class
    user_data = user_app_callback_class()
    app = GStreamerDetectionApp(app_callback, user_data)
    app.run()
