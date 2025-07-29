#!/usr/bin/env python3
"""
Debug script to test CSV functionality independently
"""

import csv
import time
import os
from datetime import datetime

def test_csv_basic():
    """Basic CSV test"""
    csv_file = "debug_test.csv"
    
    print(f"Current working directory: {os.getcwd()}")
    print(f"Attempting to create CSV file: {csv_file}")
    print(f"Absolute path: {os.path.abspath(csv_file)}")
    
    # Test 1: Create file
    try:
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Test', 'Data'])
        print("✓ Successfully created CSV file")
    except Exception as e:
        print(f"✗ Error creating CSV file: {e}")
        return False
    
    # Test 2: Append to file
    try:
        with open(csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([timestamp, 'test_data'])
        print("✓ Successfully appended to CSV file")
    except Exception as e:
        print(f"✗ Error appending to CSV file: {e}")
        return False
    
    # Test 3: Read file
    try:
        with open(csv_file, 'r') as file:
            content = file.read()
            print(f"✓ File content:\n{content}")
    except Exception as e:
        print(f"✗ Error reading CSV file: {e}")
        return False
    
    return True

def test_csv_with_same_logic():
    """Test CSV with the same logic as the main program"""
    csv_file = "debug_people_count_log.csv"
    
    print(f"\nTesting with same logic as main program...")
    print(f"File: {csv_file}")
    
    # Initialize CSV file with headers
    try:
        with open(csv_file, 'x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Minute', 'People_Count', 'Total_Unique_People'])
            print("✓ Created CSV file with headers")
    except FileExistsError:
        print("✓ CSV file already exists")
    except Exception as e:
        print(f"✗ Error creating CSV file: {e}")
        return False
    
    # Simulate logging
    tracked_people = set()
    people_count = 0
    
    for i in range(3):
        # Simulate detecting a person
        track_id = i + 1
        if track_id not in tracked_people:
            tracked_people.add(track_id)
            people_count += 1
        
        # Log to CSV (same logic as main program)
        current_time = time.time()
        minute = int(current_time // 60)
        
        try:
            with open(csv_file, 'a', newline='') as file:
                writer = csv.writer(file)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row_data = [timestamp, minute, people_count, len(tracked_people)]
                writer.writerow(row_data)
                print(f"✓ Wrote row: {row_data}")
        except Exception as e:
            print(f"✗ Error writing to CSV: {e}")
            return False
        
        time.sleep(1)
    
    # Read final content
    try:
        with open(csv_file, 'r') as file:
            content = file.read()
            print(f"✓ Final file content:\n{content}")
    except Exception as e:
        print(f"✗ Error reading final CSV file: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== CSV Debug Tests ===")
    
    # Test 1: Basic CSV functionality
    print("\n1. Basic CSV Test:")
    if test_csv_basic():
        print("✓ Basic CSV test passed")
    else:
        print("✗ Basic CSV test failed")
    
    # Test 2: Same logic as main program
    print("\n2. Main Program Logic Test:")
    if test_csv_with_same_logic():
        print("✓ Main program logic test passed")
    else:
        print("✗ Main program logic test failed")
    
    print("\n=== Debug Tests Complete ===") 