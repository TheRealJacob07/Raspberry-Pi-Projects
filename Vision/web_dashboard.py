#!/usr/bin/env python3
"""
Hailo AI People Counter - Web Dashboard
=======================================

A Flask web application that displays live charts and statistics from the people count CSV data.
Features real-time updates, interactive charts, and a responsive dashboard interface.

Features:
- Live data visualization from CSV
- Real-time chart updates
- Interactive dashboard
- Mobile-responsive design
- RESTful API endpoints

Author: Web dashboard for Hailo AI People Counter
Dependencies: Flask, pandas, plotly, dash
"""

from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly.graph_objs as go
import plotly.utils
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time
import warnings
warnings.filterwarnings('ignore')

class PeopleCounterDashboard:
    """Web dashboard for people counter data visualization."""
    
    def __init__(self, csv_file_path=None, host='0.0.0.0', port=5000):
        """
        Initialize the dashboard.
        
        Args:
            csv_file_path (str): Path to the CSV file
            host (str): Host address to bind to
            port (int): Port number to bind to
        """
        if csv_file_path is None:
            script_dir = Path(__file__).resolve().parent
            csv_file_path = script_dir / "people_count_log.csv"
        
        self.csv_file_path = Path(csv_file_path)
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.data = None
        self.last_modified = 0
        
        # Set up routes
        self.setup_routes()
        
        # Start data monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_data_changes, daemon=True)
        self.monitor_thread.start()
    
    def load_data(self):
        """Load and preprocess the CSV data."""
        try:
            if not self.csv_file_path.exists():
                print(f"CSV file not found: {self.csv_file_path}")
                return None
            
            # Check if file has been modified
            current_modified = os.path.getmtime(self.csv_file_path)
            if current_modified == self.last_modified and self.data is not None:
                return self.data
            
            print(f"DEBUG: Loading CSV file: {self.csv_file_path}")
            
            # Read CSV file, skipping comment lines
            data = pd.read_csv(self.csv_file_path, comment='#')
            
            print(f"DEBUG: Raw columns found: {list(data.columns)}")
            print(f"DEBUG: First few rows:")
            print(data.head())
            
            # Check if we have the expected number of columns
            if len(data.columns) != 8:
                print(f"WARNING: Expected 8 columns, found {len(data.columns)}")
                print(f"Columns: {list(data.columns)}")
            
            # Check if required columns exist
            required_columns = ['Timestamp', 'Minute', 'Hour', 'Day', 'People_This_Minute', 'People_This_Hour', 'People_This_Day', 'Total_Unique_People']
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                print(f"ERROR: Missing required columns: {missing_columns}")
                print(f"Available columns: {list(data.columns)}")
                
                # Try to fix common issues
                if len(data.columns) == 1 and '#' in str(data.columns[0]):
                    print("Detected malformed header. Attempting to fix...")
                    # Try reading again with different parameters
                    data = pd.read_csv(self.csv_file_path, comment='#', skip_blank_lines=True)
                    print(f"After fix attempt - columns: {list(data.columns)}")
                    
                    # Check again
                    missing_columns = [col for col in required_columns if col not in data.columns]
                    if missing_columns:
                        print(f"Still missing columns: {missing_columns}")
                        return None
                else:
                    return None
            
            # Convert timestamp to datetime
            data['Timestamp'] = pd.to_datetime(data['Timestamp'])
            
            # Add additional time-based columns for analysis
            data['Date'] = data['Timestamp'].dt.date
            data['Hour_of_Day'] = data['Timestamp'].dt.hour
            data['Minute_of_Hour'] = data['Timestamp'].dt.minute
            data['Day_of_Week'] = data['Timestamp'].dt.day_name()
            
            self.data = data
            self.last_modified = current_modified
            
            print(f"✓ Loaded {len(data)} records from {self.csv_file_path}")
            print(f"✓ Data range: {data['Timestamp'].min()} to {data['Timestamp'].max()}")
            return data
            
        except Exception as e:
            print(f"Error loading data: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _monitor_data_changes(self):
        """Monitor CSV file for changes and reload data."""
        while True:
            try:
                if self.csv_file_path.exists():
                    current_modified = os.path.getmtime(self.csv_file_path)
                    if current_modified != self.last_modified:
                        print("CSV file changed, reloading data...")
                        self.load_data()
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                print(f"Error in data monitoring: {e}")
                time.sleep(10)
    
    def setup_routes(self):
        """Set up Flask routes."""
        
        @self.app.route('/')
        def index():
            """Main dashboard page."""
            return render_template('dashboard.html')
        
        @self.app.route('/api/data')
        def get_data():
            """API endpoint to get current data."""
            data = self.load_data()
            if data is None:
                return jsonify({'error': 'Failed to load data from CSV file'})
            
            if len(data) == 0:
                return jsonify({'error': 'No data available in CSV file'})
            
            try:
                # Get latest statistics
                latest = data.iloc[-1]
                stats = {
                    'total_records': len(data),
                    'total_unique_people': int(latest['Total_Unique_People']),
                    'current_minute_people': int(latest['People_This_Minute']),
                    'current_hour_people': int(latest['People_This_Hour']),
                    'current_day_people': int(latest['People_This_Day']),
                    'last_update': latest['Timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'data_range': {
                        'start': data['Timestamp'].min().strftime('%Y-%m-%d %H:%M:%S'),
                        'end': data['Timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')
                    }
                }
                
                return jsonify(stats)
            except Exception as e:
                print(f"Error processing data: {e}")
                return jsonify({'error': f'Error processing data: {str(e)}'})
        
        @self.app.route('/api/debug/csv')
        def debug_csv():
            """Debug endpoint to check CSV file structure."""
            try:
                if not self.csv_file_path.exists():
                    return jsonify({'error': f'CSV file not found: {self.csv_file_path}'})
                
                # Read raw CSV without skipping comments
                raw_data = pd.read_csv(self.csv_file_path, header=None)
                
                # Read CSV with comments skipped
                data = pd.read_csv(self.csv_file_path, comment='#')
                
                debug_info = {
                    'file_path': str(self.csv_file_path),
                    'file_exists': True,
                    'file_size': os.path.getsize(self.csv_file_path),
                    'raw_rows': len(raw_data),
                    'processed_rows': len(data),
                    'raw_columns': list(raw_data.columns) if len(raw_data) > 0 else [],
                    'processed_columns': list(data.columns),
                    'first_few_raw_rows': raw_data.head(3).to_dict('records') if len(raw_data) > 0 else [],
                    'first_few_processed_rows': data.head(3).to_dict('records') if len(data) > 0 else []
                }
                
                return jsonify(debug_info)
            except Exception as e:
                return jsonify({'error': f'Debug error: {str(e)}'})
        
        @self.app.route('/api/chart/time_series')
        def time_series_chart():
            """API endpoint for time series chart data."""
            data = self.load_data()
            if data is None:
                return jsonify({'error': 'Failed to load data from CSV file'})
            
            if len(data) == 0:
                return jsonify({'error': 'No data available in CSV file'})
            
            try:
                # Create time series chart
                fig = go.Figure()
                
                # Add traces for different metrics
                fig.add_trace(go.Scatter(
                    x=data['Timestamp'],
                    y=data['People_This_Minute'],
                    mode='lines+markers',
                    name='People per Minute',
                    line=dict(color='blue', width=2),
                    marker=dict(size=4)
                ))
                
                fig.add_trace(go.Scatter(
                    x=data['Timestamp'],
                    y=data['People_This_Hour'],
                    mode='lines+markers',
                    name='People per Hour',
                    line=dict(color='orange', width=2),
                    marker=dict(size=4)
                ))
                
                fig.add_trace(go.Scatter(
                    x=data['Timestamp'],
                    y=data['Total_Unique_People'],
                    mode='lines+markers',
                    name='Total Unique People',
                    line=dict(color='green', width=2),
                    marker=dict(size=4)
                ))
                
                fig.update_layout(
                    title='People Detection Over Time',
                    xaxis_title='Time',
                    yaxis_title='People Count',
                    hovermode='x unified',
                    height=500
                )
                
                return jsonify(json.loads(fig.to_json()))
            except Exception as e:
                print(f"Error creating time series chart: {e}")
                return jsonify({'error': f'Error creating chart: {str(e)}'})
        
        @self.app.route('/api/chart/hourly_pattern')
        def hourly_pattern_chart():
            """API endpoint for hourly pattern chart data."""
            data = self.load_data()
            if data is None or len(data) == 0:
                return jsonify({'error': 'No data available'})
            
            # Group by hour and calculate statistics
            hourly_stats = data.groupby('Hour_of_Day').agg({
                'People_This_Hour': ['mean', 'max'],
                'Total_Unique_People': 'max'
            }).round(2)
            
            hourly_stats.columns = ['Avg_People_Per_Hour', 'Max_People_Per_Hour', 'Max_Total_Unique']
            
            fig = go.Figure()
            
            # Add bar chart for average people per hour
            fig.add_trace(go.Bar(
                x=hourly_stats.index,
                y=hourly_stats['Avg_People_Per_Hour'],
                name='Average People per Hour',
                marker_color='skyblue'
            ))
            
            fig.add_trace(go.Bar(
                x=hourly_stats.index,
                y=hourly_stats['Max_People_Per_Hour'],
                name='Maximum People per Hour',
                marker_color='lightcoral'
            ))
            
            fig.update_layout(
                title='People Detection by Hour of Day',
                xaxis_title='Hour of Day',
                yaxis_title='People Count',
                barmode='group',
                height=500
            )
            
            return jsonify(json.loads(fig.to_json()))
        
        @self.app.route('/api/chart/daily_summary')
        def daily_summary_chart():
            """API endpoint for daily summary chart data."""
            data = self.load_data()
            if data is None or len(data) == 0:
                return jsonify({'error': 'No data available'})
            
            # Group by date and calculate daily statistics
            daily_stats = data.groupby('Date').agg({
                'People_This_Day': 'max',
                'Total_Unique_People': 'max',
                'People_This_Minute': 'sum'
            }).round(2)
            
            daily_stats.columns = ['Daily_People_Count', 'Daily_Total_Unique', 'Total_Minute_Detections']
            
            fig = go.Figure()
            
            # Add bar chart for daily people count
            fig.add_trace(go.Bar(
                x=[str(d) for d in daily_stats.index],
                y=daily_stats['Daily_People_Count'],
                name='Daily People Count',
                marker_color='lightgreen'
            ))
            
            fig.add_trace(go.Bar(
                x=[str(d) for d in daily_stats.index],
                y=daily_stats['Total_Minute_Detections'],
                name='Total Minute Detections',
                marker_color='gold'
            ))
            
            fig.update_layout(
                title='Daily People Detection Summary',
                xaxis_title='Date',
                yaxis_title='People Count',
                barmode='group',
                height=500
            )
            
            return jsonify(json.loads(fig.to_json()))
        
        @self.app.route('/api/chart/heatmap')
        def heatmap_chart():
            """API endpoint for heatmap chart data."""
            data = self.load_data()
            if data is None:
                return jsonify({'error': 'Failed to load data from CSV file'})
            
            if len(data) == 0:
                return jsonify({'error': 'No data available in CSV file'})
            
            try:
                # Check if we have enough data for a heatmap
                if len(data) < 2:
                    return jsonify({'error': 'Insufficient data for heatmap (need at least 2 records)'})
                
                # Create pivot table for heatmap
                heatmap_data = data.pivot_table(
                    values='People_This_Hour', 
                    index='Day_of_Week', 
                    columns='Hour_of_Day', 
                    aggfunc='mean'
                ).fillna(0)
                
                # Check if we have any data after pivoting
                if heatmap_data.empty or heatmap_data.shape[0] == 0 or heatmap_data.shape[1] == 0:
                    return jsonify({'error': 'No valid data for heatmap after processing'})
                
                # Reorder days of week
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                heatmap_data = heatmap_data.reindex([day for day in day_order if day in heatmap_data.index])
                
                # If no days found, create a simple heatmap with available data
                if heatmap_data.empty:
                    # Create a simple heatmap with hour data only
                    hourly_avg = data.groupby('Hour_of_Day')['People_This_Hour'].mean()
                    heatmap_data = pd.DataFrame([hourly_avg.values], 
                                              index=['Current Day'], 
                                              columns=hourly_avg.index)
                
                fig = go.Figure(data=go.Heatmap(
                    z=heatmap_data.values,
                    x=heatmap_data.columns,
                    y=heatmap_data.index,
                    colorscale='YlOrRd',
                    text=heatmap_data.values.round(1),
                    texttemplate="%{text}",
                    textfont={"size": 10},
                    hoverongaps=False
                ))
                
                fig.update_layout(
                    title='People Detection Heatmap: Average Count by Hour and Day',
                    xaxis_title='Hour of Day',
                    yaxis_title='Day of Week',
                    height=500
                )
                
                return jsonify(json.loads(fig.to_json()))
            except Exception as e:
                print(f"Error creating heatmap chart: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({'error': f'Error creating heatmap: {str(e)}'})
    
    def run(self, debug=False):
        """Run the Flask application."""
        print(f"🚀 Starting Hailo AI People Counter Dashboard")
        print(f"📊 Dashboard URL: http://{self.host}:{self.port}")
        print(f"📁 Data source: {self.csv_file_path}")
        print(f"🔄 Auto-refresh: Every 5 seconds")
        print("=" * 60)
        
        self.app.run(host=self.host, port=self.port, debug=debug)

def main():
    """Main function to run the dashboard."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hailo AI People Counter Web Dashboard')
    parser.add_argument('--host', default='0.0.0.0', help='Host address (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port number (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--csv', help='Path to CSV file (default: people_count_log.csv in script directory)')
    
    args = parser.parse_args()
    
    # Create and run dashboard
    dashboard = PeopleCounterDashboard(
        csv_file_path=args.csv,
        host=args.host,
        port=args.port
    )
    
    dashboard.run(debug=args.debug)

if __name__ == "__main__":
    main() 