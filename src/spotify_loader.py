import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment Variables
load_dotenv()
print("🎯 CLIENT ID:", os.getenv("SPOTIPY_CLIENT_ID"))
print("🎯 CLIENT SECRET:", os.getenv("SPOTIPY_CLIENT_SECRET"))

class SpotifyLoader:
    def __init__(self):
        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

        # Setting up API Auth for Spotify
        self.spot = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret
        ))
    def get_track_features(self, track_id):
        """ return features given id"""
        try:
            features = self.spot.audio_features([track_id])[0]
            return features
        except Exception as e:
            print(f"error finding features for track {track_id}: {e}")
            return None
        
    def search_tracks(self, query, limit=10):
        """ search for tracks based on string input"""
        try:
            results = self.spot.search(q=query, limit=limit)
            tracks = results['tracks']['items']
            return tracks
        except Exception as e:
            print(f"Error finding tracks: {e}")
            return []
    
    def get_playlist_tracks(self, playlist_id):
        """ fetch all tracks from playlist"""
        try: 
            results = self.playlist_tracks(playlist_id)
            tracks = results['items']
        except Exception as e:
            print(f'Error finding playlist {playlist_id}: {e}')
            return []
