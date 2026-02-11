#!/usr/bin/env python3
"""
Add jobtitle_cleaned from cleaned-sgjobdata-withskills.parquet 
to cleaned-sgjobdata.parquet.
"""
import pandas as pd
import os


def main():
    source_file = "data/cleaned-sgjobdata-withskills.parquet"
    target_file = "data/cleaned-sgjobdata.parquet"
    output_file = "data/cleaned-sgjobdata.parquet"
    
    if not os.path.exists(source_file):
        print(f"Error: Source file not found: {source_file}")
        return 1
    
    if not os.path.exists(target_file):
        print(f"Error: Target file not found: {target_file}")
        return 1
    
    print(f"Loading source file: {source_file}...")
    source_df = pd.read_parquet(source_file)
    
    print(f"Loading target file: {target_file}...")
    target_df = pd.read_parquet(target_file)
    
    print(f"Source shape: {source_df.shape}")
    print(f"Target shape: {target_df.shape}")
    
    # Extract unique job_id + jobtitle_cleaned from source
    if 'jobtitle_cleaned' not in source_df.columns:
        print("Error: jobtitle_cleaned not found in source file")
        return 1
    
    # Get unique mapping of job_id -> jobtitle_cleaned
    # (source may have duplicates due to skill explosion)
    job_title_map = source_df[['job_id', 'jobtitle_cleaned']].drop_duplicates(subset=['job_id'])
    print(f"Unique job_id mappings: {len(job_title_map)}")
    
    # Drop jobtitle_cleaned from target if it exists (to avoid conflicts)
    if 'jobtitle_cleaned' in target_df.columns:
        print("Removing existing jobtitle_cleaned from target...")
        target_df = target_df.drop(columns=['jobtitle_cleaned'])
    
    # Merge into target
    print("Merging jobtitle_cleaned into target...")
    merged_df = target_df.merge(
        job_title_map,
        on='job_id',
        how='left'
    )
    
    # Verify merge
    print(f"Merged shape: {merged_df.shape}")
    print(f"Has jobtitle_cleaned: {'jobtitle_cleaned' in merged_df.columns}")
    print(f"Non-null jobtitle_cleaned: {merged_df['jobtitle_cleaned'].notna().sum()}")
    
    # Drop original uncleaned columns
    cols_to_drop = []
    if 'title' in merged_df.columns:
        cols_to_drop.append('title')
    if 'average_salary' in merged_df.columns:
        cols_to_drop.append('average_salary')
    
    if cols_to_drop:
        print(f"Dropping columns: {cols_to_drop}")
        merged_df = merged_df.drop(columns=cols_to_drop)
    
    # Final verification
    print(f"Final shape: {merged_df.shape}")
    print(f"Final columns: {list(merged_df.columns)}")
    
    # Save
    print(f"Saving to {output_file}...")
    merged_df.to_parquet(output_file, index=False)
    
    print(f"✓ Done! Updated {output_file}")
    print(f"  Rows: {len(merged_df):,}")
    print(f"  Columns: {list(merged_df.columns)}")
    
    return 0


if __name__ == "__main__":
    exit(main())
