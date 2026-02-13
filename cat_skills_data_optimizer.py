#!/usr/bin/env python3
"""
Skills Data Optimizer for High Demand Skills Chart
===================================================
This program optimizes the large skills dataset for the "High Demand Skills" chart
by removing unnecessary columns, converting dates, and pre-aggregating data.

Input:  cleaned-sgjobdata-category-withskills.parquet (~16MB)
Output: skills_optimized.parquet (~much smaller, pre-aggregated)

The optimized file contains only the necessary data:
- skill: The skill name
- category: The job category/sector
- month_year: The posting month (YYYY-MM format)
- job_count: Number of unique job postings (pre-aggregated)
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

def optimize_skills_data(input_file, output_file):
    """
    Optimize skills data by removing unnecessary columns and pre-aggregating.
    
    Args:
        input_file: Path to input parquet file
        output_file: Path to output optimized parquet file
    """
    print(f"📂 Loading data from: {input_file}")
    
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file not found: {input_file}")
        return
    
    # Load the full dataset
    df = pd.read_parquet(input_file)
    initial_size = os.path.getsize(input_file) / (1024 * 1024)  # MB
    print(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns ({initial_size:.2f} MB)")
    print(f"   Columns: {list(df.columns)}")
    
    # Keep only necessary columns
    required_columns = ['skill', 'category', 'posting_date', 'job_id']
    
    # Check if required columns exist
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        print(f"❌ Error: Missing required columns: {missing_cols}")
        return
    
    print(f"\n🔧 Processing data...")
    
    # Select only required columns
    df = df[required_columns].copy()
    print(f"   ✓ Kept only {len(required_columns)} necessary columns")
    
    # Convert posting_date to datetime and extract month_year
    df['posting_date'] = pd.to_datetime(df['posting_date'], errors='coerce')
    df = df.dropna(subset=['posting_date'])
    df['month_year'] = df['posting_date'].dt.to_period('M').astype(str)
    print(f"   ✓ Converted posting_date to month_year format (YYYY-MM)")
    
    # Drop the original posting_date column (no longer needed)
    df = df.drop(columns=['posting_date'])
    
    # Remove rows with missing critical data
    df = df.dropna(subset=['skill', 'category', 'month_year', 'job_id'])
    print(f"   ✓ Removed rows with missing data")
    
    # Aggregate: Count unique job_ids per skill, category, and month
    print(f"\n📊 Aggregating data...")
    print(f"   Before aggregation: {len(df):,} rows")
    
    aggregated_df = df.groupby(['skill', 'category', 'month_year']).agg(
        job_count=('job_id', 'nunique')
    ).reset_index()
    
    print(f"   After aggregation: {len(aggregated_df):,} rows")
    print(f"   ✓ Reduced rows by {(1 - len(aggregated_df)/len(df)) * 100:.1f}%")
    
    # Sort by month_year and skill for better compression
    aggregated_df = aggregated_df.sort_values(['month_year', 'category', 'skill'])
    
    # Add metadata
    print(f"\n📈 Summary Statistics:")
    print(f"   Unique skills: {aggregated_df['skill'].nunique():,}")
    print(f"   Unique categories: {aggregated_df['category'].nunique():,}")
    print(f"   Time period: {aggregated_df['month_year'].min()} to {aggregated_df['month_year'].max()}")
    print(f"   Total months: {aggregated_df['month_year'].nunique():,}")
    
    # Save optimized parquet file
    print(f"\n💾 Saving optimized file to: {output_file}")
    aggregated_df.to_parquet(output_file, index=False, compression='snappy')
    
    final_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
    compression_ratio = (1 - final_size / initial_size) * 100
    
    print(f"✅ Optimization complete!")
    print(f"   Original size: {initial_size:.2f} MB")
    print(f"   Optimized size: {final_size:.2f} MB")
    print(f"   Size reduction: {compression_ratio:.1f}%")
    print(f"   Speedup factor: {initial_size/final_size:.1f}x faster loading")
    
    # Display sample of optimized data
    print(f"\n📋 Sample of optimized data (first 10 rows):")
    print(aggregated_df.head(10).to_string(index=False))
    
    return aggregated_df


def main():
    """Main execution function"""
    print("=" * 70)
    print("SKILLS DATA OPTIMIZER")
    print("Optimize data for 'High Demand Skills' chart")
    print("=" * 70)
    print()
    
    # Define file paths
    script_dir = Path(__file__).parent
    data_dir = script_dir / 'data'
    
    input_file = data_dir / 'cleaned-sgjobdata-category-withskills.parquet'
    output_file = data_dir / 'skills_optimized.parquet'
    
    # Run optimization
    optimized_df = optimize_skills_data(input_file, output_file)
    
    if optimized_df is not None:
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Optimized file ready for use.")
        print("=" * 70)
        print("\n📝 Next steps:")
        print("   1. Update app.py and app_optimized.py to use 'skills_optimized.parquet'")
        print("   2. Update load_skills_data() function:")
        print("      - Change file path to 'data/skills_optimized.parquet'")
        print("      - Remove date conversion (already in month_year format)")
        print("      - Update groupby logic to use pre-aggregated job_count")
        print()


if __name__ == "__main__":
    main()
