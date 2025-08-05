"""
Hailo AI People Counter API
===========================

Flask API to serve people counter CSV data with various endpoints for data analysis.
Provides RESTful access to people detection statistics.

Endpoints:
- GET / - API information
- GET /data - All CSV data
- GET /data/latest - Latest data entry
- GET /data/summary - Summary statistics
- GET /data/hourly - Hourly aggregated data
- GET /data/daily - Daily aggregated data
- GET /data/current - Current time period data

Author: Hailo AI People Counter API
Dependencies: Flask, pandas, datetime
"""

from flask import Flask, jsonify, request
import pandas as pd
import csv
import os
from datetime import datetime, timedelta
from pathlib import Path
import json

app = Flask(__name__)

# Configuration
CSV_FILE = Path(__file__).parent.parent / "People-Counter" / "people_count_log.csv"
PORT = 8000

def load_csv_data():
    """
    Load and parse the CSV data, skipping comment lines.
    
    Returns:
        pandas.DataFrame: Parsed CSV data
    """
    try:
        # Check if CSV file exists
        if not CSV_FILE.exists():
            print(f"CSV file not found: {CSV_FILE}")
            return pd.DataFrame()
        
        # Check file permissions
        if not os.access(CSV_FILE, os.R_OK):
            print(f"Permission denied: Cannot read CSV file {CSV_FILE}")
            print("Please check file permissions or run with appropriate access")
            return pd.DataFrame()
        
        # Read CSV file, skipping comment lines that start with #
        data = []
        header_found = False
        header = None
        
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                # Skip comment lines and empty rows
                if not line or line.startswith('#') or line.startswith('"#'):
                    continue
                
                # Handle malformed CSV where header and data are concatenated
                if not header_found:
                    # Split the line to separate header from data
                    if 'Timestamp,Minute,Hour,Day,People_This_Minute,People_This_Hour,People_This_Day,Total_Unique_People' in line:
                        # Extract the data part after the header
                        data_part = line.split('Total_Unique_People', 1)[1]
                        header = ['Timestamp', 'Minute', 'Hour', 'Day', 'People_This_Minute', 'People_This_Hour', 'People_This_Day', 'Total_Unique_People']
                        header_found = True
                        
                        # Parse the data part
                        if data_part:
                            # Split by comma and create data row
                            values = data_part.split(',')
                            if len(values) >= 8:
                                data.append(values[:8])
                    else:
                        # Try to parse as regular CSV
                        row = list(csv.reader([line]))[0]
                        if len(row) >= 8:
                            header = ['Timestamp', 'Minute', 'Hour', 'Day', 'People_This_Minute', 'People_This_Hour', 'People_This_Day', 'Total_Unique_People']
                            header_found = True
                            data.append(row[:8])
                else:
                    # This is a data row
                    row = list(csv.reader([line]))[0]
                    if len(row) >= 8:
                        data.append(row[:8])
        
        if not data or not header:
            print(f"CSV file is empty or contains no valid data: {CSV_FILE}")
            return pd.DataFrame()
        
        # Create DataFrame with proper column names
        df = pd.DataFrame(data, columns=header)
        
        # Convert timestamp to datetime
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        
        # Convert numeric columns
        numeric_columns = ['Minute', 'Hour', 'Day', 'People_This_Minute', 
                          'People_This_Hour', 'People_This_Day', 'Total_Unique_People']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print(f"Successfully loaded {len(df)} records from CSV")
        return df
    except PermissionError as e:
        print(f"Permission error accessing CSV file: {e}")
        print(f"File: {CSV_FILE}")
        print("Please check file permissions or run with appropriate access")
        return pd.DataFrame()
    except FileNotFoundError as e:
        print(f"CSV file not found: {e}")
        print(f"Expected location: {CSV_FILE}")
        print("Please ensure the people counter has been run to generate data")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading CSV data: {e}")
        print(f"File: {CSV_FILE}")
        return pd.DataFrame()

@app.route('/')
def api_info():
    """
    API information endpoint.
    
    Returns:
        JSON: API information and available endpoints
    """
    return jsonify({
        'api_name': 'Hailo AI People Counter API',
        'version': '1.0.0',
        'description': 'RESTful API for accessing people counter CSV data',
        'endpoints': {
            'GET /': 'API information',
            'GET /data': 'All CSV data',
            'GET /data/latest': 'Latest data entry',
            'GET /data/summary': 'Summary statistics',
            'GET /data/hourly': 'Hourly aggregated data',
            'GET /data/daily': 'Daily aggregated data',
            'GET /data/current': 'Current time period data'
        },
        'csv_file': str(CSV_FILE),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/data')
def get_all_data():
    """
    Get all CSV data.
    
    Query Parameters:
        limit (int): Maximum number of records to return
        offset (int): Number of records to skip
    
    Returns:
        JSON: All CSV data
    """
    df = load_csv_data()
    
    if df.empty:
        return jsonify({'error': 'No data available'}), 404
    
    # Handle pagination
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int, default=0)
    
    if limit:
        df = df.iloc[offset:offset + limit]
    elif offset:
        df = df.iloc[offset:]
    
    return jsonify({
        'data': df.to_dict('records'),
        'total_records': len(df),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/data/latest')
def get_latest_data():
    """
    Get the latest data entry.
    
    Returns:
        JSON: Latest data entry
    """
    df = load_csv_data()
    
    if df.empty:
        return jsonify({'error': 'No data available'}), 404
    
    latest = df.iloc[-1].to_dict()
    
    return jsonify({
        'latest_data': latest,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/data/summary')
def get_summary():
    """
    Get summary statistics.
    
    Returns:
        JSON: Summary statistics
    """
    df = load_csv_data()
    
    if df.empty:
        return jsonify({'error': 'No data available'}), 404
    
    # Calculate summary statistics
    summary = {
        'total_records': len(df),
        'date_range': {
            'start': df['Timestamp'].min().isoformat(),
            'end': df['Timestamp'].max().isoformat()
        },
        'people_statistics': {
            'max_people_this_minute': int(df['People_This_Minute'].max()),
            'max_people_this_hour': int(df['People_This_Hour'].max()),
            'max_people_this_day': int(df['People_This_Day'].max()),
            'max_total_unique_people': int(df['Total_Unique_People'].max()),
            'avg_people_this_minute': float(df['People_This_Minute'].mean()),
            'avg_people_this_hour': float(df['People_This_Hour'].mean()),
            'avg_people_this_day': float(df['People_This_Day'].mean())
        },
        'current_totals': {
            'people_this_minute': int(df['People_This_Minute'].iloc[-1]),
            'people_this_hour': int(df['People_This_Hour'].iloc[-1]),
            'people_this_day': int(df['People_This_Day'].iloc[-1]),
            'total_unique_people': int(df['Total_Unique_People'].iloc[-1])
        }
    }
    
    return jsonify({
        'summary': summary,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/data/hourly')
def get_hourly_data():
    """
    Get hourly aggregated data.
    
    Query Parameters:
        hours (int): Number of hours to look back (default: 24)
    
    Returns:
        JSON: Hourly aggregated data
    """
    df = load_csv_data()
    
    if df.empty:
        return jsonify({'error': 'No data available'}), 404
    
    hours = request.args.get('hours', type=int, default=24)
    
    # Filter data for the specified number of hours
    cutoff_time = datetime.now() - timedelta(hours=hours)
    recent_df = df[df['Timestamp'] >= cutoff_time]
    
    if recent_df.empty:
        return jsonify({'error': f'No data available for the last {hours} hours'}), 404
    
    # Group by actual hour (0-23) from timestamp
    hourly_data = []
    for hour in range(24):
        # Get data for this hour
        hour_df = recent_df[recent_df['Timestamp'].dt.hour == hour]
        if not hour_df.empty:
            # Get the latest entry for this hour
            hour_data = hour_df.iloc[-1]
            hourly_data.append({
                'hour': hour,
                'timestamp': hour_data['Timestamp'].isoformat(),
                'people_this_hour': int(hour_data['People_This_Hour']),
                'total_unique_people': int(hour_data['Total_Unique_People'])
            })
    
    return jsonify({
        'hourly_data': hourly_data,
        'hours_analyzed': hours,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/data/daily')
def get_daily_data():
    """
    Get daily aggregated data.
    
    Query Parameters:
        days (int): Number of days to look back (default: 7)
    
    Returns:
        JSON: Daily aggregated data
    """
    df = load_csv_data()
    
    if df.empty:
        return jsonify({'error': 'No data available'}), 404
    
    days = request.args.get('days', type=int, default=7)
    
    # Filter data for the specified number of days
    cutoff_time = datetime.now() - timedelta(days=days)
    recent_df = df[df['Timestamp'] >= cutoff_time]
    
    if recent_df.empty:
        return jsonify({'error': f'No data available for the last {days} days'}), 404
    
    # Group by day and get the latest entry for each day
    daily_data = []
    for day in recent_df['Day'].unique():
        day_data = recent_df[recent_df['Day'] == day].iloc[-1]
        daily_data.append({
            'day': int(day),
            'timestamp': day_data['Timestamp'].isoformat(),
            'people_this_day': int(day_data['People_This_Day']),
            'total_unique_people': int(day_data['Total_Unique_People'])
        })
    
    return jsonify({
        'daily_data': daily_data,
        'days_analyzed': days,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/data/current')
def get_current_data():
    """
    Get current time period data (current minute, hour, day).
    
    Returns:
        JSON: Current time period data
    """
    df = load_csv_data()
    
    if df.empty:
        return jsonify({'error': 'No data available'}), 404
    
    # Get current time periods
    now = datetime.now()
    current_minute = int(now.timestamp() // 60)
    current_hour = int(now.timestamp() // 3600)
    current_day = int(now.timestamp() // 86400)
    
    # Get the latest data entry
    latest = df.iloc[-1]
    
    current_data = {
        'current_time': now.isoformat(),
        'current_periods': {
            'minute': current_minute,
            'hour': current_hour,
            'day': current_day
        },
        'latest_data': {
            'timestamp': latest['Timestamp'].isoformat(),
            'people_this_minute': int(latest['People_This_Minute']),
            'people_this_hour': int(latest['People_This_Hour']),
            'people_this_day': int(latest['People_This_Day']),
            'total_unique_people': int(latest['Total_Unique_People'])
        }
    }
    
    return jsonify({
        'current_data': current_data,
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print(f"Starting Hailo AI People Counter API on port {PORT}")
    print(f"CSV file: {CSV_FILE}")
    print(f"CSV file exists: {CSV_FILE.exists()}")
    if CSV_FILE.exists():
        print(f"CSV file readable: {os.access(CSV_FILE, os.R_OK)}")
    print(f"API will be available at: http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=PORT, debug=False) 