import requests
import pandas as pd
import time
import re
import lyricsgenius
from langdetect import detect
import os
import json
from datetime import datetime
import sys

# API Configuration
GENIUS_API_KEY = "r6vW9hyUck05RRuvBF4L1f5MjirVAeuHO0tauARd-aB1pt7xscCUVzMnFoFC2WTS"
DISCOGS_TOKEN = "xmWNqVMtvKoFllImiTkEbgIMpgmdVRVggXqrWJPQ"

# Headers for different APIs
MUSICBRAINZ_HEADERS = {
    "User-Agent": "milestone/1.0 (smacieje@umich.edu)"
}
DISCOGS_HEADERS = {"User-Agent": "TrackFetcher/1.0"}

# Target years for data collection
TARGET_YEARS = [2007, 2008, 2009, 2020, 2025]

# Initialize Genius client
genius = lyricsgenius.Genius(GENIUS_API_KEY)
genius.remove_section_headers = False

def log_progress(message):
    """Log progress with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def save_checkpoint(data, filename):
    """Save data checkpoint to avoid losing progress."""
    try:
        if isinstance(data, pd.DataFrame):
            data.to_csv(filename, index=False)
        else:
            with open(filename, 'w') as f:
                json.dump(data, f)
        log_progress(f"Checkpoint saved: {filename}")
    except Exception as e:
        log_progress(f"Error saving checkpoint {filename}: {e}")

def load_checkpoint(filename):
    """Load data checkpoint if it exists."""
    if os.path.exists(filename):
        try:
            if filename.endswith('.csv'):
                return pd.read_csv(filename)
            else:
                with open(filename, 'r') as f:
                    return json.load(f)
        except Exception as e:
            log_progress(f"Error loading checkpoint {filename}: {e}")
    return None

# MusicBrainz Functions
def get_releases_by_year(year, limit=50):
    """Fetches releases from MusicBrainz for a specific year."""
    url = "https://musicbrainz.org/ws/2/release/"
    params = {
        "query": f"date:[{year}-01-01 TO {year}-12-31]",
        "fmt": "json",
        "limit": limit
    }
    
    try:
        response = requests.get(url, headers=MUSICBRAINZ_HEADERS, params=params)
        response.raise_for_status()
        return response.json().get("releases", [])
    except Exception as e:
        log_progress(f"Error fetching releases for {year}: {e}")
        return []

def get_tracks_from_release(release_id):
    """Fetches all tracks (recordings) from a given MusicBrainz release."""
    url = f"https://musicbrainz.org/ws/2/release/{release_id}"
    params = {
        "inc": "recordings+artist-credits",
        "fmt": "json"
    }
    
    try:
        response = requests.get(url, headers=MUSICBRAINZ_HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        
        release_title = data.get("title")
        release_date = data.get("date")
        album_artist = data["artist-credit"][0]["name"] if "artist-credit" in data else None

        tracks = []
        for medium in data.get("media", []):
            for track in medium.get("tracks", []):
                # Use track artist if available, otherwise album artist
                track_artist = track["artist-credit"][0]["name"] if track.get("artist-credit") else album_artist
                
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
    except Exception as e:
        log_progress(f"Error fetching tracks for release {release_id}: {e}")
        return []

def get_musicbrainz_tracks_by_year(year, release_limit=50, delay=1.1):
    """Get all tracks from MusicBrainz for a given year with checkpointing."""
    checkpoint_file = f"musicbrainz_{year}_checkpoint.csv"
    
    # Check for existing checkpoint
    existing_data = load_checkpoint(checkpoint_file)
    if existing_data is not None and not existing_data.empty:
        log_progress(f"Resuming from checkpoint for MusicBrainz {year}")
        return existing_data
    
    log_progress(f"Starting MusicBrainz data collection for {year}")
    releases = get_releases_by_year(year, limit=release_limit)
    all_tracks = []

    for i, release in enumerate(releases):
        release_id = release["id"]
        tracks = get_tracks_from_release(release_id)
        all_tracks.extend(tracks)
        
        time.sleep(delay)  # Be polite to the MusicBrainz servers
        
        # Progress update every 10 releases
        if (i + 1) % 10 == 0:
            log_progress(f"MusicBrainz {year}: Processed {i + 1}/{len(releases)} releases")
            # Save intermediate checkpoint
            if all_tracks:
                temp_df = pd.DataFrame(all_tracks)
                save_checkpoint(temp_df, checkpoint_file)
    
    df = pd.DataFrame(all_tracks)
    save_checkpoint(df, checkpoint_file)
    log_progress(f"MusicBrainz {year}: Collected {len(df)} tracks")
    return df

# Discogs Functions
def get_discogs_release_tracks(release_id):
    """Get tracks from a specific Discogs release."""
    url = f"https://api.discogs.com/releases/{release_id}"
    params = {"token": DISCOGS_TOKEN}
    
    try:
        response = requests.get(url, headers=DISCOGS_HEADERS, params=params)
        if response.status_code != 200:
            return []
            
        data = response.json()
        tracks = []
        
        for track in data.get("tracklist", []):
            if track.get("type_") == "track":
                tracks.append({
                    "release_id": release_id,
                    "album": data.get("title"),
                    "title": track.get("title"),
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
    except Exception as e:
        log_progress(f"Error fetching Discogs release {release_id}: {e}")
        return []

def search_discogs_tracks_by_year(year, per_page=50, max_pages=5, delay=1.2):
    """Search Discogs for tracks released in a specific year with pagination."""
    checkpoint_file = f"discogs_{year}_checkpoint.csv"
    
    # Check for existing checkpoint
    existing_data = load_checkpoint(checkpoint_file)
    if existing_data is not None and not existing_data.empty:
        log_progress(f"Resuming from checkpoint for Discogs {year}")
        return existing_data
    
    log_progress(f"Starting Discogs data collection for {year}")
    search_url = "https://api.discogs.com/database/search"
    all_tracks = []
    
    for page in range(1, max_pages + 1):
        params = {
            "token": DISCOGS_TOKEN,
            "year": year,
            "type": "release",
            "format": "Album",
            "per_page": per_page,
            "page": page
        }

        try:
            response = requests.get(search_url, headers=DISCOGS_HEADERS, params=params)
            results = response.json().get("results", [])
            
            if not results:
                break
            
            for i, result in enumerate(results):
                release_id = result.get("id")
                if release_id:
                    tracks = get_discogs_release_tracks(release_id)
                    all_tracks.extend(tracks)
                    time.sleep(delay)  # Respect rate limits
                
                # Progress update
                if (i + 1) % 10 == 0:
                    log_progress(f"Discogs {year} Page {page}: Processed {i + 1}/{len(results)} releases")
            
            log_progress(f"Discogs {year}: Completed page {page}/{max_pages}")
            
            # Save checkpoint after each page
            if all_tracks:
                temp_df = pd.DataFrame(all_tracks)
                save_checkpoint(temp_df, checkpoint_file)
            
        except Exception as e:
            log_progress(f"Error on Discogs page {page} for {year}: {e}")
            break

    df = pd.DataFrame(all_tracks)
    save_checkpoint(df, checkpoint_file)
    log_progress(f"Discogs {year}: Collected {len(df)} tracks")
    return df

# Genius Functions
def search_genius_lyrics(song_title, artist_name):
    """Search for lyrics on Genius and return cleaned lyrics."""
    try:
        song = genius.search_song(song_title, artist_name)
        if song:
            lyrics = song.lyrics
            # Clean lyrics by removing everything after "Read More" or "Embed"
            lyrics = re.split(r'(Read More|Embed)', lyrics)[0].strip()
            return lyrics
        return None
    except Exception as e:
        return None

def safe_language_detect(text):
    """Safely detect language of text, returning 'unknown' if detection fails."""
    try:
        if text and isinstance(text, str) and len(text.strip()) > 0:
            return detect(text)
        return "unknown"
    except:
        return "unknown"

def add_lyrics_to_dataframe(df, delay=1.0, checkpoint_interval=50):
    """Add lyrics and language detection to a DataFrame with robust error handling."""
    if df.empty:
        return df
    
    # Check for existing lyrics checkpoint
    lyrics_checkpoint = "lyrics_checkpoint.csv"
    if os.path.exists(lyrics_checkpoint):
        log_progress("Resuming lyrics collection from checkpoint")
        checkpoint_df = pd.read_csv(lyrics_checkpoint)
        if len(checkpoint_df) == len(df) and 'lyrics' in checkpoint_df.columns:
            log_progress("Lyrics collection already completed")
            return checkpoint_df
    
    log_progress(f"Starting lyrics collection for {len(df)} tracks")
    
    lyrics_list = []
    for idx, row in df.iterrows():
        song_title = row.get("title", "")
        artist_name = row.get("artist", "")
        
        if song_title and artist_name:
            lyrics = search_genius_lyrics(song_title, artist_name)
        else:
            lyrics = None
            
        lyrics_list.append(lyrics)
        
        if delay > 0:
            time.sleep(delay)
        
        # Progress indicator and checkpoint saving
        if (idx + 1) % checkpoint_interval == 0:
            log_progress(f"Lyrics progress: {idx + 1}/{len(df)} tracks processed")
            # Save intermediate checkpoint
            temp_df = df.copy()
            temp_df["lyrics"] = lyrics_list + [None] * (len(df) - len(lyrics_list))
            save_checkpoint(temp_df, lyrics_checkpoint)
    
    # Add lyrics to DataFrame
    df["lyrics"] = lyrics_list
    
    # Add language detection
    log_progress("Detecting languages...")
    df["language"] = df["lyrics"].apply(safe_language_detect)
    
    return df

def collect_all_music_data():
    """Main function to collect all music data for target years."""
    log_progress("Starting comprehensive music data collection")
    log_progress(f"Target years: {TARGET_YEARS}")
    
    all_dataframes = []
    
    for year in TARGET_YEARS:
        log_progress(f"Processing year {year}")
        
        # Collect MusicBrainz data
        try:
            mb_df = get_musicbrainz_tracks_by_year(year, release_limit=100)
            if not mb_df.empty:
                all_dataframes.append(mb_df)
        except Exception as e:
            log_progress(f"Error collecting MusicBrainz data for {year}: {e}")
        
        # Collect Discogs data
        try:
            discogs_df = search_discogs_tracks_by_year(year, per_page=50, max_pages=10)
            if not discogs_df.empty:
                all_dataframes.append(discogs_df)
        except Exception as e:
            log_progress(f"Error collecting Discogs data for {year}: {e}")
        
        # Small delay between years
        time.sleep(2)
    
    # Combine all data
    if all_dataframes:
        log_progress("Combining all data sources...")
        combined_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
        
        # Remove duplicates based on title and artist
        initial_count = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=['title', 'artist'], keep='first')
        log_progress(f"Removed {initial_count - len(combined_df)} duplicates")
        
        # Add lyrics
        log_progress("Adding lyrics to combined dataset...")
        final_df = add_lyrics_to_dataframe(combined_df)
        
        # Save final results
        output_filename = f"music_data_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        final_df.to_csv(output_filename, index=False)
        log_progress(f"Final dataset saved: {output_filename}")
        log_progress(f"Total tracks collected: {len(final_df)}")
        
        return final_df
    else:
        log_progress("No data collected")
        return pd.DataFrame()

def get_year_summary():
    """Print summary of data collection progress."""
    log_progress("Data collection summary:")
    for year in TARGET_YEARS:
        mb_file = f"musicbrainz_{year}_checkpoint.csv"
        discogs_file = f"discogs_{year}_checkpoint.csv"
        
        mb_count = 0
        discogs_count = 0
        
        if os.path.exists(mb_file):
            try:
                mb_df = pd.read_csv(mb_file)
                mb_count = len(mb_df)
            except:
                pass
        
        if os.path.exists(discogs_file):
            try:
                discogs_df = pd.read_csv(discogs_file)
                discogs_count = len(discogs_df)
            except:
                pass
        
        log_progress(f"Year {year}: MusicBrainz={mb_count}, Discogs={discogs_count}")

# Main execution
if __name__ == "__main__":
    try:
        # Check if running summary mode
        if len(sys.argv) > 1 and sys.argv[1] == "summary":
            get_year_summary()
        else:
            # Run full data collection
            final_dataset = collect_all_music_data()
            get_year_summary()
            
    except KeyboardInterrupt:
        log_progress("Process interrupted by user")
        get_year_summary()
    except Exception as e:
        log_progress(f"Unexpected error: {e}")
        get_year_summary()
