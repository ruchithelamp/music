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

def extract_musicbrainz_metadata(file_path):
    """Extracts relevant fields from a MusicBrainz-style JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    releases = data.get('releases', [])
    rows = []

    for r in releases:
        artist_names = " & ".join([ac.get("name") for ac in r.get("artist-credit", [])])
        label_names = ", ".join([li["label"]["name"] for li in r.get("label-info", []) if "label" in li])
        label_catalog = ", ".join([li.get("catalog-number", "") for li in r.get("label-info", [])])
        country = r.get("country")
        release_date = r.get("date")
        title = r.get("title")
        primary_type = r.get("release-group", {}).get("primary-type")
        secondary_types = ", ".join(r.get("release-group", {}).get("secondary-types", []))
        media_formats = ", ".join([m.get("format", "Unknown") for m in r.get("media", [])])

        row = {
            "release_id": r.get("id"),
            "title": title,
            "artist": artist_names,
            "date": release_date,
            "country": country,
            "primary_type": primary_type,
            "secondary_types": secondary_types,
            "format": media_formats,
            "label": label_names,
            "catalog_number": label_catalog,
            "barcode": r.get("barcode"),
            "asin": r.get("asin"),
            "track_count": r.get("track-count"),
            "source": "musicbrainz"
        }

        rows.append(row)

    return pd.DataFrame(rows)

def load_all_musicbrainz_json(folder_path):
    """Iterates through a folder and extracts metadata from each MusicBrainz JSON file."""
    all_dfs = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            full_path = os.path.join(folder_path, filename)
            try:
                df = extract_musicbrainz_metadata(full_path)
                all_dfs.append(df)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

def main():
    parser = argparse.ArgumentParser(description='Merge and convert JSON dataframes from multiple files')
    parser.add_argument('--input-folder', '-i', required=True, help='Directories containing JSON files')
    parser.add_argument('--output', '-o', required=True, help='Output CSV file path')
    args = parser.parse_args()

    merged_df = load_all_musicbrainz_json(args.input_folder)

    if merged_df.empty:
        print("No valid dataframes were created.")
        sys.exit(1)

    merged_df.to_csv(args.output, index=False)
    print(f"Saved merged dataframe to {args.output}")

if __name__ == "__main__":
    main()
