import pandas as pd
import lyricsgenius
import time
import os
import argparse
import sys

def fetch_lyrics(genius, artist, title, delay=1.0):
    try:
        print(f"Searching for: {artist} - {title}")
        
        song = genius.search_song(title, artist)
        
        if song:
            print(f"Found lyrics for: {artist} - {title}")
            time.sleep(delay)
            return song.lyrics
        else:
            print(f"No lyrics found for: {artist} - {title}")
            time.sleep(delay)
            return None
            
    except Exception as e:
        print(f"Error fetching lyrics for {artist} - {title}: {str(e)}")
        time.sleep(delay)
        return None

# CLI args
def main():
    parser = argparse.ArgumentParser(description='Fetch lyrics from Genius API for songs in CSV file')
    parser.add_argument('input_file', help='Input CSV file path')
    parser.add_argument('--output', default='songs_with_lyrics.csv', help='Output CSV file path')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between API requests (seconds)')
    parser.add_argument('--checkpoint-interval', type=int, default=5, help='Save progress every N songs')
    parser.add_argument('--token', help='Genius API token (or set GENIUS_TOKEN environment variable)')
    
    args = parser.parse_args()
    
    GENIUS_TOKEN = "r6vW9hyUck05RRuvBF4L1f5MjirVAeuHO0tauARd-aB1pt7xscCUVzMnFoFC2WTS"
    INPUT_FILE = args.input_file
    OUTPUT_FILE = args.output
    DELAY_BETWEEN_REQUESTS = args.delay
    CHECKPOINT_INTERVAL = args.checkpoint_interval
    
    if GENIUS_TOKEN == "r6vW9hyUck05RRuvBF4L1f5MjirVAeuHO0tauARd-aB1pt7xscCUVzMnFoFC2WTS":
        print("ERROR: Genius API token not set!")
        print("Set it using --token argument or GENIUS_TOKEN environment variable")
        print("Get your token from: https://genius.com/api-clients")
        sys.exit(1)
    
    genius = lyricsgenius.Genius(GENIUS_TOKEN)
    genius.skip_non_songs = False
    
    try:
        df = pd.read_csv(INPUT_FILE)
        print(f"Loaded {len(df)} songs from {INPUT_FILE}")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    df['lyrics'] = ""
    df['lyrics_found'] = False
    
    for index, row in df.iterrows():
        artist = row['artist']
        title = row['title']
        
        print(f"\nProcessing {index + 1}/{len(df)}: {artist} - {title}")
        
        lyrics = fetch_lyrics(genius, artist, title, DELAY_BETWEEN_REQUESTS)
        
        if lyrics:
            df.at[index, 'lyrics'] = lyrics
            df.at[index, 'lyrics_found'] = True
        else:
            df.at[index, 'lyrics'] = ""
            df.at[index, 'lyrics_found'] = False
        
        # CHeckpoint saves
        if (index + 1) % CHECKPOINT_INTERVAL == 0:
            df.to_csv(OUTPUT_FILE, index=False)
            print(f"Progress saved to {OUTPUT_FILE} ({index + 1}/{len(df)} completed)")
    
    # Final save
    df.to_csv(OUTPUT_FILE, index=False)

if __name__ == "__main__":
    
    main()
