"""
MusicBrainz batch job script for HPC
Collects track data from MusicBrainz API and saves to CSV
"""

import requests
import pandas as pd
import time
import sys
import argparse
from pathlib import Path

HEADERS = {
    "User-Agent": "milestone/1.0 (smacieje@umich.edu)"  # Replace with your contact info
}

def get_all_releases_by_year(year, limit_per_request=100):
    """Fetches ALL releases from MusicBrainz for a specific year using pagination."""
    url = "https://musicbrainz.org/ws/2/release/"
    all_releases = []
    offset = 0
    
    while True:
        params = {
            "query": f"date:[{year}-01-01 TO {year}-12-31]",
            "fmt": "json",
            "limit": limit_per_request,
            "offset": offset
        }
        
        print(f"Fetching releases {offset} to {offset + limit_per_request - 1}")
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        
        releases = data.get("releases", [])
        if not releases:
            break
            
        all_releases.extend(releases)
        
        # Check if we've got all releases
        if len(releases) < limit_per_request:
            break
            
        offset += limit_per_request
        time.sleep(1.1)  # Rate limiting between pagination requests
    
    return all_releases

def get_tracks_from_release(release_id):
    """Fetches all tracks (recordings) from a given release."""
    url = f"https://musicbrainz.org/ws/2/release/{release_id}"
    params = {
        "inc": "recordings+artist-credits",
        "fmt": "json"
    }
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()
    
    release_title = data.get("title")
    release_date = data.get("date")
    artist = data["artist-credit"][0]["name"] if "artist-credit" in data else None

    tracks = []
    for medium in data.get("media", []):
        for track in medium.get("tracks", []):
            # Fixed the duplicate "artist" key issue from original code
            track_artist = track["artist-credit"][0]["name"] if track.get("artist-credit") else artist
            tracks.append({
                "title": track.get("title"),
                "track_length_ms": track.get("length"),
                "album": release_title,
                "release_date": release_date,
                "artist": track_artist,
                "MBID": track.get("id"),
                "source": "musicbrainz"
            })
    return tracks

def get_tracks_by_year(year, delay=1.1, checkpoint_interval=100, output_dir="."):
    """Main function to get ALL tracks released in a given year."""
    print(f"Fetching ALL releases for year {year}...")
    releases = get_all_releases_by_year(year)
    print(f"Found {len(releases)} total releases for {year}")
    
    all_tracks = []
    checkpoint_path = Path(output_dir) / f"musicbrainz_tracks_{year}_checkpoint.csv"
    
    for i, release in enumerate(releases):
        release_id = release["id"]
        try:
            print(f"Processing release {i+1}/{len(releases)}: {release.get('title', 'Unknown')}")
            tracks = get_tracks_from_release(release_id)
            all_tracks.extend(tracks)
            
            # Checkpoint save
            if (i + 1) % checkpoint_interval == 0:
                df_temp = pd.DataFrame(all_tracks)
                df_temp.to_csv(checkpoint_path, index=False)
                print(f"Checkpoint saved: {len(all_tracks)} tracks so far")
            
            time.sleep(delay)  # Be polite to the MusicBrainz servers
            
        except Exception as e:
            print(f"Error fetching tracks for release {release_id}: {e}")
            continue
    
    print(f"Collected {len(all_tracks)} total tracks for {year}")
    return pd.DataFrame(all_tracks)

def main():
    parser = argparse.ArgumentParser(description='Fetch ALL MusicBrainz data for a given year')
    parser.add_argument('year', type=int, help='Year to fetch data for')
    parser.add_argument('--output-dir', type=str, default='.', help='Output directory')
    parser.add_argument('--delay', type=float, default=1.1, help='Delay between API calls')
    parser.add_argument('--checkpoint-interval', type=int, default=100, help='Save checkpoint every N releases')
    
    args = parser.parse_args()
    
    try:
        # Create output directory if it doesn't exist
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Get ALL the tracks
        df = get_tracks_by_year(args.year, delay=args.delay, 
                               checkpoint_interval=args.checkpoint_interval,
                               output_dir=args.output_dir)
        
        # Save final CSV
        output_path = Path(args.output_dir) / f"musicbrainz_tracks_{args.year}.csv"
        df.to_csv(output_path, index=False)
        print(f"Final data saved to {output_path}")
        print(f"Final dataset shape: {df.shape}")
        
        # Clean up checkpoint file
        checkpoint_path = Path(args.output_dir) / f"musicbrainz_tracks_{args.year}_checkpoint.csv"
        if checkpoint_path.exists():
            checkpoint_path.unlink()
            print("Checkpoint file cleaned up")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()