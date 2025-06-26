"""
Genius Lyrics batch job script for HPC
Reads track data from CSV files and adds lyrics from Genius API
"""

import re
import pandas as pd
import time
import sys
import argparse
from pathlib import Path
import lyricsgenius

GENIUS_API_KEY = "r6vW9hyUck05RRuvBF4L1f5MjirVAeuHO0tauARd-aB1pt7xscCUVzMnFoFC2WTS"

def search_genius_lyrics(song_title, artist_name, max_retries=3, delay=1.0):
    """Search for lyrics with retry logic and error handling."""
    genius = lyricsgenius.Genius(GENIUS_API_KEY)
    genius.remove_section_headers = False
    genius.timeout = 15  # Set timeout for requests
    
    for attempt in range(max_retries):
        try:
            song = genius.search_song(song_title, artist_name)
            
            if song:
                # Clean up lyrics - remove everything after "Embed" or "Read More"
                lyrics = song.lyrics
                return lyrics
            else:
                return None
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for '{song_title}' by '{artist_name}': {e}")
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))  # Exponential backoff
            else:
                print(f"All attempts failed for '{song_title}' by '{artist_name}'")
                return None
    
    return None

def process_lyrics_batch(df, delay=1.2, checkpoint_interval=50, output_path=None):
    """Process lyrics in batches with checkpointing."""
    total_tracks = len(df)
    print(f"Processing lyrics for {total_tracks} tracks")
    
    # Add lyrics column if it doesn't exist
    if 'lyrics' not in df.columns:
        df['lyrics'] = None
    
    # Track progress
    processed_count = 0
    success_count = 0
    
    for idx, row in df.iterrows():
        # Skip if lyrics already exist (for resuming interrupted jobs)
        if pd.notna(row.get('lyrics')):
            processed_count += 1
            success_count += 1
            continue
        
        # Get track info (handle different column names from different sources)
        song_title = row.get('track_title') or row.get('title')
        artist_name = row.get('artist')
        
        if not song_title or not artist_name:
            print(f"Skipping row {idx}: missing title or artist")
            processed_count += 1
            continue
        
        print(f"Processing {processed_count + 1}/{total_tracks}: '{song_title}' by '{artist_name}'")
        
        # Search for lyrics
        lyrics = search_genius_lyrics(song_title, artist_name)
        df.at[idx, 'lyrics'] = lyrics
        
        if lyrics:
            success_count += 1
            print(f"  ✓ Found lyrics ({len(lyrics)} characters)")
        else:
            print(f"  ✗ No lyrics found")
        
        processed_count += 1
        
        # Checkpoint save
        if processed_count % checkpoint_interval == 0 and output_path:
            print(f"Checkpoint: saving progress at {processed_count}/{total_tracks}")
            df.to_csv(output_path, index=False)
        
        # Rate limiting
        time.sleep(delay)
    
    success_rate = (success_count / total_tracks) * 100 if total_tracks > 0 else 0
    print(f"Completed: {success_count}/{total_tracks} tracks with lyrics ({success_rate:.1f}%)")
    
    return df

def main():
    parser = argparse.ArgumentParser(description='Add Genius lyrics to track data')
    parser.add_argument('input_file', type=str, help='Input CSV file with track data')
    parser.add_argument('--output-file', type=str, help='Output CSV file (default: adds _with_lyrics suffix)')
    parser.add_argument('--delay', type=float, default=1.5, help='Delay between API calls')
    parser.add_argument('--checkpoint-interval', type=int, default=50, help='Save progress every N tracks')
    parser.add_argument('--start-row', type=int, default=0, help='Start processing from this row (for resuming)')
    parser.add_argument('--max-rows', type=int, help='Maximum number of rows to process')
    
    args = parser.parse_args()
    
    # Input validation
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist")
        sys.exit(1)
    
    # Output path
    if args.output_file:
        output_path = Path(args.output_file)
    else:
        output_path = input_path.parent / f"{input_path.stem}_with_lyrics{input_path.suffix}"
    
    try:
        print(f"Loading data from {input_path}")
        df = pd.read_csv(input_path)
        print(f"Loaded {len(df)} tracks")
        
        # Slice dataframe if needed
        if args.start_row > 0 or args.max_rows:
            end_row = args.start_row + args.max_rows if args.max_rows else len(df)
            df = df.iloc[args.start_row:end_row].copy()
            print(f"Processing rows {args.start_row} to {end_row-1} ({len(df)} tracks)")
        
        # Process lyrics
        df_with_lyrics = process_lyrics_batch(
            df, 
            delay=args.delay,
            checkpoint_interval=args.checkpoint_interval,
            output_path=output_path
        )
        
        # Final save
        df_with_lyrics.to_csv(output_path, index=False)
        print(f"Final results saved to {output_path}")
        print(f"Dataset shape: {df_with_lyrics.shape}")
        
        # Summary statistics
        lyrics_found = df_with_lyrics['lyrics'].notna().sum()
        print(f"Lyrics found for {lyrics_found}/{len(df_with_lyrics)} tracks")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
