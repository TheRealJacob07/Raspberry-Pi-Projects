#!/usr/bin/env python3
"""
Test script to verify CSV logging functionality
"""

import csv
import time
from datetime import datetime

def test_csv_logging():
    """Test the CSV logging functionality"""
    csv_file = "test_people_count_log.csv"
    
    # Initialize CSV file with headers
    try:
        with open(csv_file, 'x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Minute', 'People_Count', 'Total_Unique_People'])
        print(f"Created new CSV file: {csv_file}")
    except FileExistsError:
        print(f"CSV file already exists: {csv_file}")
    
    # Simulate some logging
    tracked_people = set()
    people_count = 0
    
    # Simulate detecting people
    for i in range(5):
        track_id = i + 1
        if track_id not in tracked_people:
            tracked_people.add(track_id)
            people_count += 1
        
        # Log to CSV
        current_time = time.time()
        minute = int(current_time // 60)
        
        with open(csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([timestamp, minute, people_count, len(tracked_people)])
        
        print(f"Logged: People in this minute: {people_count}, Total unique: {len(tracked_people)}")
        time.sleep(1)  # Simulate time passing
    
    print(f"Test completed. Check {csv_file} for results.")

if __name__ == "__main__":
    test_csv_logging() 