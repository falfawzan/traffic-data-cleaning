#!/usr/bin/env python3
"""
Validation script for data cleaning pipeline outputs.

This script validates that the pipeline has produced expected outputs
and checks data quality metrics.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import sqlite3

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "data-cleaning-and-fusion-tool" / "Code" / "src"))

def validate_file_exists(filepath, description):
    """Validate that a file exists."""
    if Path(filepath).exists():
        size = Path(filepath).stat().st_size / (1024**2)  # MB
        print(f"✅ {description}: {filepath} ({size:.2f} MB)")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def validate_csv(filepath, min_rows=0, required_columns=None):
    """Validate CSV file structure."""
    try:
        df = pd.read_csv(filepath, nrows=1000)  # Sample for validation
        row_count = sum(1 for _ in open(filepath)) - 1  # Full count
        
        if row_count < min_rows:
            print(f"⚠️  {filepath}: Only {row_count} rows (expected at least {min_rows})")
            return False
        
        if required_columns:
            missing = set(required_columns) - set(df.columns)
            if missing:
                print(f"❌ {filepath}: Missing columns: {missing}")
                return False
        
        print(f"✅ {filepath}: {row_count:,} rows, {len(df.columns)} columns")
        return True
    except Exception as e:
        print(f"❌ {filepath}: Error reading file - {e}")
        return False

def validate_database(db_path):
    """Validate SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"✅ Database: {len(tables)} tables found")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count:,} rows")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database validation failed: {e}")
        return False

def main():
    """Main validation function."""
    print("=" * 60)
    print("Data Cleaning Pipeline Output Validation")
    print("=" * 60)
    print()
    
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "data" / "output"
    
    results = []
    
    # Validate cleaned data files
    print("Validating Cleaned Data Files:")
    print("-" * 60)
    results.append(validate_file_exists(
        output_dir / "cleaned_data" / "waypoint_cleaned_mapmatched.csv",
        "Waypoint Map-Matched Data"
    ))
    results.append(validate_file_exists(
        output_dir / "cleaned_data" / "trajs_cleaned.csv",
        "Trip Path Cleaned Data"
    ))
    
    # Validate CSV structure
    if results[-2]:  # If waypoint file exists
        validate_csv(
            output_dir / "cleaned_data" / "waypoint_cleaned_mapmatched.csv",
            min_rows=1000,
            required_columns=["journey_id", "latitude", "longitude", "speed_mph", "local_time"]
        )
    
    if results[-1]:  # If trajs file exists
        validate_csv(
            output_dir / "cleaned_data" / "trajs_cleaned.csv",
            min_rows=100,
            required_columns=["SegmentId", "CrossingSpeedMph", "CrossingStartDateLocal"]
        )
    
    print()
    
    # Validate quality metrics
    print("Validating Quality Metrics:")
    print("-" * 60)
    results.append(validate_file_exists(
        output_dir / "quality_metrics" / "cleaning_impact_summary.csv",
        "Cleaning Impact Summary"
    ))
    results.append(validate_file_exists(
        output_dir / "quality_metrics" / "completeness_metrics.csv",
        "Completeness Metrics"
    ))
    results.append(validate_file_exists(
        output_dir / "quality_metrics" / "speed_statistics.csv",
        "Speed Statistics"
    ))
    results.append(validate_file_exists(
        output_dir / "quality_metrics" / "performance_metrics.csv",
        "Performance Metrics"
    ))
    
    print()
    
    # Validate visualizations
    print("Validating Visualizations:")
    print("-" * 60)
    figure_files = [
        "input_vs_cleaned_comparison.png",
        "speed_distribution_analysis.png",
        "cross_source_validation.png",
        "completeness_analysis.png"
    ]
    for fig in figure_files:
        results.append(validate_file_exists(
            output_dir / "figures" / fig,
            f"Figure: {fig}"
        ))
    
    print()
    
    # Validate database
    print("Validating Database:")
    print("-" * 60)
    db_path = output_dir / "database" / "unified_database.db"
    if db_path.exists():
        validate_database(db_path)
    else:
        print(f"⚠️  Database not found: {db_path}")
        print("   (Database may be gitignored if large)")
    
    print()
    print("=" * 60)
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"Validation Summary: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ All validations passed!")
        return 0
    else:
        print("⚠️  Some validations failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

