# Vision People Counter

This enhanced version of the Hailo detection application now includes people counting functionality with CSV logging.

## Features

- **Real-time People Detection**: Detects people in video frames using Hailo AI
- **Unique People Tracking**: Tracks unique individuals using track IDs to avoid double counting
- **Minute-by-Minute Logging**: Logs people count data to CSV file every minute
- **Visual Display**: Shows current frame people count and total unique people on video frames

## How It Works

### People Counting Logic
1. **Detection**: The system detects people in each video frame
2. **Tracking**: Each detected person gets a unique track ID from the Hailo system
3. **Deduplication**: The system maintains a set of seen track IDs to count each person only once
4. **Counting**: New people (new track IDs) increment the total count

### CSV Logging
- **File**: `people_count_log.csv` (created in the same directory as the script)
- **Frequency**: Every minute
- **Columns**:
  - `Timestamp`: Human-readable date and time
  - `Minute`: Minute since epoch (for easy grouping)
  - `People_Count`: Number of people detected in that minute
  - `Total_Unique_People`: Cumulative count of unique people seen

### CSV File Format
```csv
Timestamp,Minute,People_Count,Total_Unique_People
2024-01-15 14:30:00,1234567,3,5
2024-01-15 14:31:00,1234568,2,7
2024-01-15 14:32:00,1234569,0,7
```

## Usage

1. **Run the main program**:
   ```bash
   python main.py
   ```

2. **Monitor the output**:
   - Console will show detection information
   - Video frames will display current counts
   - CSV file will be updated every minute

3. **Check the CSV file**:
   ```bash
   cat people_count_log.csv
   ```

## Testing

Run the test script to verify CSV functionality:
```bash
python test_csv_logging.py
```

## Configuration

### CSV File Location
The CSV file is created in the same directory as `main.py`. You can modify the `csv_file` variable in the `user_app_callback_class.__init__()` method to change the location.

### Logging Frequency
Currently set to log every 60 seconds. You can modify the condition in `app_callback()`:
```python
if current_time - user_data.last_log_time >= 60:  # Change 60 to desired seconds
```

## Technical Details

### Thread Safety
- CSV operations are protected with a threading lock to prevent corruption
- The callback function runs in a separate thread from the main application

### Memory Management
- Track IDs are stored in a set for efficient lookup
- The set persists for the entire session (resets when program restarts)

### Error Handling
- CSV write errors are caught and logged to console
- The program continues running even if CSV logging fails

## Dependencies

- All original Hailo dependencies
- Standard Python libraries: `csv`, `time`, `threading`, `datetime`

## Notes

- The system counts people who have walked through the frame at least once
- Track IDs are used to identify unique individuals
- The CSV file is created automatically on first run
- Previous CSV data is preserved when the program restarts 