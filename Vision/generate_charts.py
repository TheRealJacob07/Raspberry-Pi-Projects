#!/usr/bin/env python3
"""
Hailo AI People Counter - Chart Generator
=========================================

This script generates various charts and visualizations from the people count CSV data.
It creates time series charts, bar charts, heatmaps, and summary statistics.

Features:
- Time series analysis of people detection
- Hourly and daily traffic patterns
- Peak activity identification
- Trend analysis
- Interactive charts (if matplotlib supports it)

Author: Chart generator for Hailo AI People Counter
Dependencies: pandas, matplotlib, seaborn, numpy
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class PeopleCounterChartGenerator:
    """Generate charts and visualizations from people count CSV data."""
    
    def __init__(self, csv_file_path=None):
        """
        Initialize the chart generator.
        
        Args:
            csv_file_path (str): Path to the CSV file. If None, uses default location.
        """
        if csv_file_path is None:
            # Use default location in the same directory as this script
            script_dir = Path(__file__).resolve().parent
            csv_file_path = script_dir / "people_count_log.csv"
        
        self.csv_file_path = Path(csv_file_path)
        self.data = None
        self.load_data()
        
        # Set up matplotlib style
        plt.style.use('default')
        sns.set_palette("husl")
        
    def load_data(self):
        """Load and preprocess the CSV data."""
        try:
            # First, try to read the file and see what we get
            print(f"DEBUG: Attempting to read CSV file: {self.csv_file_path}")
            
            # Read CSV file, skipping comment lines
            self.data = pd.read_csv(self.csv_file_path, comment='#')
            
            # Debug: Print column names to see what we actually have
            print(f"DEBUG: Found columns: {list(self.data.columns)}")
            print(f"DEBUG: First few rows:")
            print(self.data.head())
            
            # Check if we have the expected number of columns
            if len(self.data.columns) != 8:
                print(f"WARNING: Expected 8 columns, found {len(self.data.columns)}")
                print(f"Columns: {list(self.data.columns)}")
            
            # Check if required columns exist
            required_columns = ['Timestamp', 'Minute', 'Hour', 'Day', 'People_This_Minute', 'People_This_Hour', 'People_This_Day', 'Total_Unique_People']
            missing_columns = [col for col in required_columns if col not in self.data.columns]
            
            if missing_columns:
                print(f"ERROR: Missing required columns: {missing_columns}")
                print(f"Available columns: {list(self.data.columns)}")
                
                # Try to fix common issues
                if len(self.data.columns) == 1 and '#' in str(self.data.columns[0]):
                    print("Detected malformed header. Attempting to fix...")
                    # Try reading again with different parameters
                    self.data = pd.read_csv(self.csv_file_path, comment='#', skip_blank_lines=True)
                    print(f"After fix attempt - columns: {list(self.data.columns)}")
                    
                    # Check again
                    missing_columns = [col for col in required_columns if col not in self.data.columns]
                    if missing_columns:
                        print(f"Still missing columns: {missing_columns}")
                        return
                else:
                    return
            
            # Convert timestamp to datetime
            self.data['Timestamp'] = pd.to_datetime(self.data['Timestamp'])
            
            # Add additional time-based columns for analysis
            self.data['Date'] = self.data['Timestamp'].dt.date
            self.data['Hour_of_Day'] = self.data['Timestamp'].dt.hour
            self.data['Minute_of_Hour'] = self.data['Timestamp'].dt.minute
            self.data['Day_of_Week'] = self.data['Timestamp'].dt.day_name()
            
            print(f"✓ Loaded {len(self.data)} records from {self.csv_file_path}")
            print(f"✓ Data range: {self.data['Timestamp'].min()} to {self.data['Timestamp'].max()}")
            
        except FileNotFoundError:
            print(f"❌ Error: CSV file not found at {self.csv_file_path}")
            print("Please run the main.py script first to generate data.")
            return
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            print(f"DEBUG: Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            return
    
    def create_time_series_chart(self, save_path=None):
        """Create a time series chart showing people detection over time."""
        if self.data is None or len(self.data) == 0:
            print("❌ No data available for charting")
            return
        
        # Validate required columns exist
        required_columns = ['Timestamp', 'People_This_Minute', 'People_This_Hour', 'Total_Unique_People']
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        if missing_columns:
            print(f"❌ Missing required columns for time series chart: {missing_columns}")
            return
        
        plt.figure(figsize=(15, 8))
        
        # Create subplots for different metrics
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12))
        
        # Plot 1: People per minute over time
        ax1.plot(self.data['Timestamp'], self.data['People_This_Minute'], 
                marker='o', markersize=3, linewidth=1, alpha=0.7)
        ax1.set_title('People Detection per Minute Over Time', fontsize=14, fontweight='bold')
        ax1.set_ylabel('People Count')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Plot 2: People per hour over time
        ax2.plot(self.data['Timestamp'], self.data['People_This_Hour'], 
                marker='s', markersize=4, linewidth=2, alpha=0.8, color='orange')
        ax2.set_title('People Detection per Hour Over Time', fontsize=14, fontweight='bold')
        ax2.set_ylabel('People Count')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        # Plot 3: Total unique people over time
        ax3.plot(self.data['Timestamp'], self.data['Total_Unique_People'], 
                marker='^', markersize=4, linewidth=2, alpha=0.8, color='green')
        ax3.set_title('Total Unique People Over Time', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Total Unique People')
        ax3.set_xlabel('Time')
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Time series chart saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def create_hourly_pattern_chart(self, save_path=None):
        """Create a chart showing hourly traffic patterns."""
        if self.data is None or len(self.data) == 0:
            print("❌ No data available for charting")
            return
        
        # Group by hour and calculate statistics
        hourly_stats = self.data.groupby('Hour_of_Day').agg({
            'People_This_Hour': ['mean', 'max', 'sum'],
            'Total_Unique_People': 'max'
        }).round(2)
        
        hourly_stats.columns = ['Avg_People_Per_Hour', 'Max_People_Per_Hour', 'Total_People_Per_Hour', 'Max_Total_Unique']
        
        plt.figure(figsize=(12, 8))
        
        # Create subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Plot 1: Average people per hour
        hours = hourly_stats.index
        ax1.bar(hours, hourly_stats['Avg_People_Per_Hour'], 
               color='skyblue', alpha=0.7, edgecolor='navy')
        ax1.set_title('Average People Detection by Hour of Day', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Hour of Day')
        ax1.set_ylabel('Average People Count')
        ax1.set_xticks(range(0, 24))
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate(hourly_stats['Avg_People_Per_Hour']):
            ax1.text(i, v + 0.1, f'{v:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Plot 2: Maximum people per hour
        ax2.bar(hours, hourly_stats['Max_People_Per_Hour'], 
               color='lightcoral', alpha=0.7, edgecolor='darkred')
        ax2.set_title('Maximum People Detection by Hour of Day', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Maximum People Count')
        ax2.set_xticks(range(0, 24))
        ax2.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate(hourly_stats['Max_People_Per_Hour']):
            ax2.text(i, v + 0.1, f'{v:.0f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Hourly pattern chart saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def create_daily_summary_chart(self, save_path=None):
        """Create a chart showing daily summary statistics."""
        if self.data is None or len(self.data) == 0:
            print("❌ No data available for charting")
            return
        
        # Group by date and calculate daily statistics
        daily_stats = self.data.groupby('Date').agg({
            'People_This_Day': 'max',
            'Total_Unique_People': 'max',
            'People_This_Minute': 'sum'
        }).round(2)
        
        daily_stats.columns = ['Daily_People_Count', 'Daily_Total_Unique', 'Total_Minute_Detections']
        
        plt.figure(figsize=(14, 10))
        
        # Create subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
        
        # Plot 1: Daily people count
        dates = [str(d) for d in daily_stats.index]
        ax1.bar(dates, daily_stats['Daily_People_Count'], 
               color='lightgreen', alpha=0.7, edgecolor='darkgreen')
        ax1.set_title('Daily People Detection Summary', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Daily People Count')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate(daily_stats['Daily_People_Count']):
            ax1.text(i, v + 0.1, f'{v:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Plot 2: Total minute detections per day
        ax2.bar(dates, daily_stats['Total_Minute_Detections'], 
               color='gold', alpha=0.7, edgecolor='orange')
        ax2.set_title('Total Minute-by-Minute Detections per Day', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Total Detections')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate(daily_stats['Total_Minute_Detections']):
            ax2.text(i, v + 0.1, f'{v:.0f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Daily summary chart saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def create_heatmap(self, save_path=None):
        """Create a heatmap showing people detection patterns by hour and day."""
        if self.data is None or len(self.data) == 0:
            print("❌ No data available for charting")
            return
        
        # Create pivot table for heatmap
        heatmap_data = self.data.pivot_table(
            values='People_This_Hour', 
            index='Day_of_Week', 
            columns='Hour_of_Day', 
            aggfunc='mean'
        ).fillna(0)
        
        # Reorder days of week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex([day for day in day_order if day in heatmap_data.index])
        
        plt.figure(figsize=(16, 8))
        
        # Create heatmap
        sns.heatmap(heatmap_data, 
                   annot=True, 
                   fmt='.1f', 
                   cmap='YlOrRd', 
                   cbar_kws={'label': 'Average People Count'})
        
        plt.title('People Detection Heatmap: Average Count by Hour and Day of Week', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Hour of Day', fontsize=12)
        plt.ylabel('Day of Week', fontsize=12)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Heatmap saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def create_summary_statistics(self, save_path=None):
        """Create a summary statistics table and chart."""
        if self.data is None or len(self.data) == 0:
            print("❌ No data available for charting")
            return
        
        # Calculate summary statistics
        stats = {
            'Total Records': len(self.data),
            'Date Range': f"{self.data['Timestamp'].min().strftime('%Y-%m-%d')} to {self.data['Timestamp'].max().strftime('%Y-%m-%d')}",
            'Total Unique People': self.data['Total_Unique_People'].max(),
            'Max People in One Minute': self.data['People_This_Minute'].max(),
            'Max People in One Hour': self.data['People_This_Hour'].max(),
            'Max People in One Day': self.data['People_This_Day'].max(),
            'Average People per Minute': self.data['People_This_Minute'].mean(),
            'Average People per Hour': self.data['People_This_Hour'].mean(),
            'Peak Hour': self.data.loc[self.data['People_This_Hour'].idxmax(), 'Hour_of_Day'],
            'Total Detections': self.data['People_This_Minute'].sum()
        }
        
        # Create summary chart
        plt.figure(figsize=(12, 8))
        
        # Create subplot for key metrics
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Plot 1: Key metrics bar chart
        metrics = ['Max People\n(Minute)', 'Max People\n(Hour)', 'Max People\n(Day)', 'Total Unique\nPeople']
        values = [stats['Max People in One Minute'], 
                 stats['Max People in One Hour'], 
                 stats['Max People in One Day'], 
                 stats['Total Unique People']]
        
        bars = ax1.bar(metrics, values, color=['lightblue', 'lightgreen', 'lightcoral', 'gold'])
        ax1.set_title('Key Detection Metrics', fontsize=14, fontweight='bold')
        ax1.set_ylabel('People Count')
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Plot 2: Average metrics
        avg_metrics = ['Avg People\n(Minute)', 'Avg People\n(Hour)', 'Peak Hour']
        avg_values = [stats['Average People per Minute'], 
                     stats['Average People per Hour'], 
                     stats['Peak Hour']]
        
        bars2 = ax2.bar(avg_metrics, avg_values, color=['skyblue', 'orange', 'red'])
        ax2.set_title('Average Metrics and Peak Hour', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Count / Hour')
        ax2.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars2, avg_values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Summary statistics chart saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
        
        # Print summary statistics
        print("\n" + "="*60)
        print("SUMMARY STATISTICS")
        print("="*60)
        for key, value in stats.items():
            print(f"{key:<25}: {value}")
        print("="*60)
    
    def generate_all_charts(self, output_dir=None):
        """Generate all charts and save them to the specified directory."""
        if output_dir is None:
            output_dir = Path(__file__).resolve().parent / "charts"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        print(f"\n📊 Generating charts and saving to: {output_dir}")
        print("-" * 50)
        
        try:
            # Generate all charts
            self.create_time_series_chart(output_dir / "time_series_chart.png")
            self.create_hourly_pattern_chart(output_dir / "hourly_pattern_chart.png")
            self.create_daily_summary_chart(output_dir / "daily_summary_chart.png")
            self.create_heatmap(output_dir / "heatmap.png")
            self.create_summary_statistics(output_dir / "summary_statistics.png")
            
            print(f"\n✅ All charts generated successfully!")
            print(f"📁 Charts saved in: {output_dir}")
            
        except Exception as e:
            print(f"❌ Error generating charts: {e}")

def main():
    """Main function to run the chart generator."""
    print("🎯 Hailo AI People Counter - Chart Generator")
    print("=" * 50)
    
    # Initialize chart generator
    generator = PeopleCounterChartGenerator()
    
    # Check if data was loaded successfully
    if generator.data is None:
        print("❌ Failed to load data. Please check the CSV file and try again.")
        return
    
    if len(generator.data) == 0:
        print("❌ No data available in CSV file. Please run main.py first to generate data.")
        return
    
    # Check if we have the required columns
    required_columns = ['Timestamp', 'Minute', 'Hour', 'Day', 'People_This_Minute', 'People_This_Hour', 'People_This_Day', 'Total_Unique_People']
    missing_columns = [col for col in required_columns if col not in generator.data.columns]
    
    if missing_columns:
        print(f"❌ CSV file is missing required columns: {missing_columns}")
        print(f"Available columns: {list(generator.data.columns)}")
        print("Please ensure the CSV file was generated by the latest version of main.py")
        return
    
    print(f"✅ Data loaded successfully: {len(generator.data)} records")
    
    # Generate all charts
    generator.generate_all_charts()
    
    # Also show summary statistics
    generator.create_summary_statistics()

if __name__ == "__main__":
    main() 