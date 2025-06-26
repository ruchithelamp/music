"""
Discogs batch job script for HPC
Collects track data from Discogs API and saves to CSV
"""

import requests
import pandas as pd
import time
import sys
import argparse
from pathlib import Path

DISCOGS_TOKEN = "xmWNqVMtvKoFllImiTkEbgIMpgmdVRVggXqrWJPQ"
HEADERS = {"User-Agent": "TrackFetcher/1.0"}

def get_release_tracks(release_id):
    """Get tracks from a specific Discogs release."""
    url = f"https://api.discogs.com/releases/{release_id}"
    params = {"token": DISCOGS_TOKEN}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch release {release_id}: {response.status_code}")
        return []
    
    data = response.json()
    tracks = []
    for track in data.get("tracklist", []):
        if track.get("type_") == "track":
            tracks.append({
                "release_id": release_id,
                "album_title": data.get("title"),
                "track_title": track.get("title"),
                "track_position": track.get("position"),
                "duration": track.get("duration"),
                "year": data.get("year"),
                "country": data.get("country"),
                "genre": ", ".join(data.get("genres", [])),
                "style": ", ".join(data.get("styles", [])),
                "artist": ", ".join([artist['name'] for artist in data.get("artists", [])]),
                "source": "discogs"
            })
    return tracks

def search_discogs_tracks_by_year(year, per_page=10, max_pages=5, delay=1.2):
    """Search for tracks by year with pagination support."""
    search_url = "https://api.discogs.com/database/search"
    all_tracks = []
    
    for page in range(1, max_pages + 1):
        print(f"Fetching page {page}/{max_pages} for year {year}")
        
        params = {
            "token": DISCOGS_TOKEN,
            "year": year,
            "type": "release",
            "format": "Album",
            "per_page": per_page,
            "page": page
        }

        try:
            response = requests.get(search_url, headers=HEADERS, params=params)
            response.raise_for_status()
            results = response.json().get("results", [])
            
            if not results:
                print(f"No more results found at page {page}")
                break
            
            print(f"Processing {len(results)} releases from page {page}")
            
            for i, r in enumerate(results):
                release_id = r.get("id")
                if release_id:
                    print(f"  Processing release {i+1}/{len(results)}: {r.get('title', 'Unknown')}")
                    tracks = get_release_tracks(release_id)
                    all_tracks.extend(tracks)
                    time.sleep(delay)  # Respect rate limits
            
        except Exception as e:
            print(f"Error processing page {page}: {e}")
            continue
    
    print(f"Collected {len(all_tracks)} total tracks")
    return pd.DataFrame(all_tracks)

def main():
    parser = argparse.ArgumentParser(description='Fetch Discogs data for a given year')
    parser.add_argument('year', type=int, help='Year to fetch data for')
    parser.add_argument('--per-page', type=int, default=20, help='Results per page')
    parser.add_argument('--max-pages', type=int, default=5, help='Maximum pages to fetch')
    parser.add_argument('--output-dir', type=str, default='.', help='Output directory')
    parser.add_argument('--delay', type=float, default=1.2, help='Delay between API calls')
    
    args = parser.parse_args()
    
    try:
        # Get the tracks
        df = search_discogs_tracks_by_year(
            args.year, 
            per_page=args.per_page, 
            max_pages=args.max_pages, 
            delay=args.delay
        )
        
        # Save to CSV
        output_path = Path(args.output_dir) / f"discogs_tracks_{args.year}.csv"
        df.to_csv(output_path, index=False)
        print(f"Data saved to {output_path}")
        print(f"Final dataset shape: {df.shape}")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
