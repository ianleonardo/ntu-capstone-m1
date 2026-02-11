#!/usr/bin/env python3
"""
Extract and explode skills data from cleaned-sgjobdata-withskills.parquet.
Creates cleaned-sgjobdata-category-withskills.parquet with job_id, category, posting_date, skill.
"""
import pandas as pd
import json
import os
import sys


def parse_categories(cat_str):
    """Parse category JSON string into list."""
    try:
        if isinstance(cat_str, str):
            return json.loads(cat_str.replace("'", '"'))
        return []
    except Exception:
        return []


def extract_category(val):
    """Extract category name from dict or string."""
    if isinstance(val, dict):
        return val.get('category', val.get('name', str(val)))
    return str(val)


def main():
    source_file = "data/cleaned-sgjobdata-withskills.parquet"
    output_file = "data/cleaned-sgjobdata-category-withskills.parquet"
    
    if not os.path.exists(source_file):
        print(f"Error: Source file not found: {source_file}")
        return 1
    
    print(f"Loading {source_file}...", flush=True)
    df = pd.read_parquet(source_file, columns=['job_id', 'categories', 'posting_date', 'skill'])
    
    print(f"Source shape: {df.shape}", flush=True)
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB", flush=True)
    
    # Explode categories - process in-place to save memory
    print("Parsing categories...", flush=True)
    df['parsed_categories'] = df['categories'].apply(parse_categories)
    
    # Drop original categories column to save memory
    df = df.drop(columns=['categories'])
    
    print("Exploding categories...", flush=True)
    df = df.explode('parsed_categories')
    
    print("Extracting category names...", flush=True)
    df['category'] = df['parsed_categories'].apply(extract_category)
    
    # Drop intermediate column
    df = df.drop(columns=['parsed_categories'])
    
    # Remove rows with empty/null categories
    print("Filtering empty categories...", flush=True)
    df = df[df['category'].notna() & (df['category'] != '')]
    
    # Reorder columns
    df = df[['job_id', 'category', 'posting_date', 'skill']]
    
    print(f"After category explosion: {df.shape}", flush=True)
    print(f"Final columns: {list(df.columns)}", flush=True)
    print(f"Unique categories: {df['category'].nunique()}", flush=True)
    print(f"Unique skills: {df['skill'].nunique()}", flush=True)
    
    # Save
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    print(f"Saving to {output_file}...", flush=True)
    df.to_parquet(output_file, index=False)
    
    print(f"\n✓ Done! Created {output_file}", flush=True)
    print(f"  Rows: {len(df):,}", flush=True)
    print(f"  Columns: {list(df.columns)}", flush=True)
    print(f"\n  Sample:", flush=True)
    print(df.head(3).to_string(), flush=True)
    
    return 0


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        exit(130)
    except Exception as e:
        print(f"\n\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        exit(1)
