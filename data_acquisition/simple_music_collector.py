import requests
import json
import time
import os
from pathlib import Path
import lyricsgenius

# API Tokens - Replace with your actual tokens
DISCOGS_TOKEN = "xmWNqVMtvKoFllImiTkEbgIMpgmdVRVggXqrWJPQ"
GENIUS_API_TOKEN = "r6vW9hyUck05RRuvBF4L1f5MjirVAeuHO0tauARd-aB1pt7xscCUVzMnFoFC2WTS"

# Create output directories
def setup_directories():
    for year in [2007, 2008, 2009, 2020, 2025]:
        for api in ['discogs', 'musicbrainz', 'acousticbrainz', 'genius']:
            Path(f"music_data/{year}/{api}").mkdir(parents=True, exist_ok=True)

def get_discogs_data(year, page=1, per_page=100):
    """Get Discogs releases for a specific year and page"""
    url = "https://api.discogs.com/database/search"
    headers = {"User-Agent": "MusicDataCollector/1.0"}
    params = {
        "token": DISCOGS_TOKEN,
        "year": year,
        "type": "release",
        "per_page": per_page,
        "page": page
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Discogs API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting Discogs data: {e}")
        return None

def get_musicbrainz_data(year, offset=0, limit=100):
    """Get MusicBrainz releases for a specific year"""
    url = "https://musicbrainz.org/ws/2/release"
    headers = {"User-Agent": "milestone/1.0 (smacieje@umich.edu)"}
    params = {
        "query": f"date:[{year}-01-01 TO {year}-12-31]",
        "fmt": "json",
        "limit": limit,
        "offset": offset,
        "inc": "artist-credits+recordings+genres+tags"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"MusicBrainz API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting MusicBrainz data: {e}")
        return None

def get_acousticbrainz_data(mbid):
    """Get AcousticBrainz features for a specific MBID"""
    url = f"https://acousticbrainz.org/api/v1/{mbid}/high-level"
    headers = {"User-Agent": "MusicDataCollector/1.0"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

def search_genius_song(artist, title):
    """Search for a song on Genius and get lyrics"""
    try:
        genius = lyricsgenius.Genius(GENIUS_API_KEY)
        genius.verbose = False  # Turn off status messages
        genius.remove_section_headers = True
        
        # Search for the song
        song = genius.search_song(title, artist)
        if song:
            # Clean up lyrics like in your original approach
            lyrics = song.lyrics
            import re
            lyrics = re.split(r'(Read More|Embed)', lyrics)[0].strip()
            
            return {
                "title": song.title,
                "artist": song.artist,
                "lyrics": lyrics,  # Full lyrics text
                "url": song.url,
                "genius_id": song.id,
                "raw_song_data": {
                    "title": song.title,
                    "artist": song.artist,
                    "album": getattr(song, 'album', None),
                    "year": getattr(song, 'year', None),
                    "stats": getattr(song, 'stats', None)
                }
            }
        return None
    except Exception as e:
        print(f"Error searching Genius for '{artist} - {title}': {e}")
        return None

def collect_discogs_year(year, max_pages=None):
    """Collect all Discogs data for a year"""
    print(f"Collecting Discogs data for {year}...")
    page = 1
    total_collected = 0
    
    while True:
        if max_pages and page > max_pages:
            break
            
        print(f"  Page {page}...")
        data = get_discogs_data(year, page=page, per_page=100)
        
        if not data or not data.get('results'):
            print(f"  No more results at page {page}")
            break
        
        # Save the raw JSON
        filename = f"music_data/{year}/discogs/page_{page:04d}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        total_collected += len(data['results'])
        print(f"  Saved {len(data['results'])} releases (Total: {total_collected})")
        
        # Check if we've reached the end
        pagination = data.get('pagination', {})
        if page >= pagination.get('pages', 1):
            break
        
        page += 1
        time.sleep(1)  # Rate limiting
    
    print(f"Discogs {year}: Collected {total_collected} releases")

def collect_musicbrainz_year(year, max_requests=None):
    """Collect all MusicBrainz data for a year"""
    print(f"Collecting MusicBrainz data for {year}...")
    offset = 0
    limit = 100
    total_collected = 0
    request_count = 0
    
    while True:
        if max_requests and request_count >= max_requests:
            break
            
        print(f"  Offset {offset}...")
        data = get_musicbrainz_data(year, offset=offset, limit=limit)
        
        if not data or not data.get('releases'):
            print(f"  No more results at offset {offset}")
            break
        
        # Save the raw JSON
        filename = f"music_data/{year}/musicbrainz/offset_{offset:06d}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        releases_count = len(data['releases'])
        total_collected += releases_count
        print(f"  Saved {releases_count} releases (Total: {total_collected})")
        
        # Check if we've reached the end
        if releases_count < limit:
            break
        
        offset += limit
        request_count += 1
        time.sleep(1.1)  # MusicBrainz requires 1 second between requests
    
    print(f"MusicBrainz {year}: Collected {total_collected} releases")

def collect_acousticbrainz_from_musicbrainz(year, max_files=None):
    """Collect AcousticBrainz data using MBIDs from MusicBrainz files"""
    print(f"Collecting AcousticBrainz data for {year}...")
    
    mb_dir = Path(f"music_data/{year}/musicbrainz")
    mb_files = list(mb_dir.glob("*.json"))
    
    if max_files:
        mb_files = mb_files[:max_files]
    
    total_collected = 0
    
    for mb_file in mb_files:
        print(f"  Processing {mb_file.name}...")
        
        with open(mb_file, 'r', encoding='utf-8') as f:
            mb_data = json.load(f)
        
        for release in mb_data.get('releases', []):
            mbid = release.get('id')
            if not mbid:
                continue
            
            # Check if we already have this data
            ab_filename = f"music_data/{year}/acousticbrainz/{mbid}.json"
            if os.path.exists(ab_filename):
                continue
            
            ab_data = get_acousticbrainz_data(mbid)
            if ab_data:
                with open(ab_filename, 'w', encoding='utf-8') as f:
                    json.dump(ab_data, f, indent=2, ensure_ascii=False)
                total_collected += 1
            
            time.sleep(0.1)  # Small delay to be nice to the API
    
    print(f"AcousticBrainz {year}: Collected {total_collected} features")

def collect_genius_from_musicbrainz(year, max_songs=None):
    """Collect Genius data using song info from MusicBrainz files"""
    if max_songs:
        print(f"Collecting Genius data for {year} (limited to {max_songs} songs)...")
    else:
        print(f"Collecting ALL available Genius data for {year}...")
        print("Note: Only ~1% of songs will have lyrics (1.5M lyrics vs 150M+ releases)")
    
    mb_dir = Path(f"music_data/{year}/musicbrainz")
    mb_files = list(mb_dir.glob("*.json"))
    
    collected_count = 0
    attempted_count = 0
    not_found_count = 0
    
    for mb_file in mb_files:
        if max_songs and collected_count >= max_songs:
            break
            
        with open(mb_file, 'r', encoding='utf-8') as f:
            mb_data = json.load(f)
        
        for release in mb_data.get('releases', []):
            if max_songs and collected_count >= max_songs:
                break
                
            # Extract artist info
            artist_name = ""
            if release.get('artist-credit'):
                artist_name = release['artist-credit'][0].get('name', '')
            
            # Look for recordings/tracks
            if 'media' in release:
                for medium in release['media']:
                    if max_songs and collected_count >= max_songs:
                        break
                    if 'tracks' in medium:
                        for track in medium['tracks']:
                            if max_songs and collected_count >= max_songs:
                                break
                            if 'recording' in track:
                                recording = track['recording']
                                title = recording.get('title', '')
                                recording_id = recording.get('id', '')
                                
                                if title and artist_name and recording_id:
                                    # Check if we already have this
                                    genius_filename = f"music_data/{year}/genius/{recording_id}.json"
                                    if os.path.exists(genius_filename):
                                        continue
                                    
                                    attempted_count += 1
                                    print(f"  Searching ({attempted_count}): {artist_name} - {title}")
                                    genius_data = search_genius_song(artist_name, title)
                                    
                                    if genius_data and genius_data.get('lyrics'):
                                        with open(genius_filename, 'w', encoding='utf-8') as f:
                                            json.dump(genius_data, f, indent=2, ensure_ascii=False)
                                        collected_count += 1
                                        print(f"    ✓ Found lyrics! ({collected_count} found, {not_found_count} not found)")
                                    else:
                                        not_found_count += 1
                                        if attempted_count % 100 == 0:  # Progress update every 100 attempts
                                            print(f"    Progress: {collected_count} found, {not_found_count} not found")
                                    
                                    time.sleep(1)  # Rate limiting for Genius
    
    success_rate = (collected_count / attempted_count * 100) if attempted_count > 0 else 0
    print(f"Genius {year}: Found {collected_count} lyrics out of {attempted_count} attempts ({success_rate:.1f}% success rate)")
    print(f"Expected: ~1% success rate based on Genius/Discogs ratio")

def main():
    """Main collection function - FULL COLLECTION"""
    setup_directories()
    
    # Years to collect
    years = [2007, 2008, 2009, 2020, 2025]
    
    print("=== Music Data Collection Started ===")
    print("FULL COLLECTION - No limits (will take ~7 hours)")
    print("You can stop anytime with Ctrl+C and resume later.")
    print()
    
    for year in years:
        print(f"\n--- Collecting data for {year} ---")
        
        # Collect ALL Discogs data
        collect_discogs_year(year)
        
        # Collect ALL MusicBrainz data
        collect_musicbrainz_year(year)
        
        # Collect ALL available Genius lyrics (most won't have lyrics anyway)
        collect_genius_from_musicbrainz(year)
        
        print(f"--- Completed {year} ---")
    
    print("\n=== Collection Complete! ===")
    print("Check the music_data/ directory for all JSON files")

if __name__ == "__main__":
    # Test with small amounts first
    # setup_directories()
    # print("Testing with year 2020...")
    # collect_discogs_year(2020, max_pages=2)
    # collect_musicbrainz_year(2020, max_requests=2)
    
    main()
