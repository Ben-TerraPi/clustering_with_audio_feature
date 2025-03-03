from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
from tqdm import tqdm

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = "http://localhost:8080/callback"

# Authentification
client_credentials_manager = SpotifyClientCredentials(client_id = SPOTIPY_CLIENT_ID, client_secret = SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

# Test authentification
try:
    token = sp.auth_manager.get_access_token(as_dict=False)
    print(f"✅ Authentification réussie !")
except Exception as e:
    print(f"❌ Erreur d'authentification : {e}")

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Fonctions

def get_track_id(artist, track):
    try:
        result = sp.search(q=f'artist:{artist} track:{track}', type='track', limit=1)
        time.sleep(1)  # rate limit

        if result['tracks']['items']:
            return result['tracks']['items'][0]['id']
        else:
            return None
    except Exception as e:
        print(f"Erreur pour {artist} - {track}: {e}")
        return None

def add_spotify_ids_to_csv(input_file_path, output_file_path):
    df = pd.read_csv(input_file_path)
    print("Récupération des spotify_id")

    # Ajout colonne pour ID + barre de progression
    tqdm.pandas()
    df['spotify_id'] = df.progress_apply(lambda row: get_track_id(row['artist'], row['title']), axis=1)

    # Sauvegarde nouveau csv
    df.to_csv(output_file_path, index=False)

    print(f"Les IDs Spotify ont été ajoutés et sauvegardés dans {output_file_path}")
    

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


add_spotify_ids_to_csv('my_tracks.csv', 'spotify/my_tracks_spotify_ids.csv')