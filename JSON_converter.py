#!/usr/bin/env python3
"""
Converter Script
Converts raw JSON files to CSV for dataframe analysis
"""

import pandas as pd
import json
import argparse
import os
import sys

def extract_release_metadata(file_path):
    """Extract selected release metadata from a Discogs JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    releases = data.get('results', [])
    rows = []

    for r in releases:
        row = {
            "release_id": r.get("id"),
            "album_title": r.get("title").split(" - ")[1] if " - " in r.get("title", "") else None,
            "artist": r.get("title").split(" - ")[0] if " - " in r.get("title", "") else None,
            "year": r.get("year"),
            "country": r.get("country"),
            "duration": r.get("duration"),
            "genre": ", ".join(r.get("genre", [])),
            "style": ", ".join(r.get("style", [])),
            "source": "discogs"
        }
        rows.append(row)

    return pd.DataFrame(rows)

def load_and_combine_json(json_dirs):
    """Process all JSON files in given directories and combine them."""
    all_dfs = []

    for json_dir in json_dirs:
        for filename in os.listdir(json_dir):
            if filename.endswith(".json"):
                full_path = os.path.join(json_dir, filename)
                try:
                    df = extract_release_metadata(full_path)
                    all_dfs.append(df)
                except Exception as e:
                    print(f"Error processing {filename}: {e}")

    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
    
def main():
    parser = argparse.ArgumentParser(description='Merge and convert JSON dataframes from multiple files')
    parser.add_argument('--JSON-dirs', nargs='+', required=True, help='Directories containing JSON files')
    parser.add_argument('--output', '-o', required=True, help='Output CSV file path')
    
    args = parser.parse_args()

    merged_df = load_and_combine_json(args.JSON_dirs)

    if merged_df.empty:
        print("No valid dataframes were created.")
        sys.exit(1)

    # Save to CSV
    merged_df.to_csv(args.output, index=False)
    print(f"Saved merged dataframe to {args.output}")

if __name__ == "__main__":
    main()
