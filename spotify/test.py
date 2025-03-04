from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
from tqdm import tqdm
import re
from fuzzywuzzy import fuzz
from unidecode import unidecode

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

def test_track_id(track_id):
    try:
        # Récupérer les informations du track à partir de son ID
        track_info = sp.track(track_id)

        # Afficher les informations du track
        print(f"Track Name: {track_info['name']}")
        print(f"Artist: {track_info['artists'][0]['name']}")
        print(f"Album: {track_info['album']['name']}")
        print(f"Duration (ms): {track_info['duration_ms']}")
        print(f"Popularity: {track_info['popularity']}")
        print(f"Preview URL: {track_info['preview_url']}")

    except Exception as e:
        print(f"Erreur lors de la récupération des informations du track avec l'ID {track_id}: {e}")

# Exemple d'utilisation
track_id_to_test = "2LQTHb4rEtKpxQgeqdesmc"  # Remplacez par l'ID que vous souhaitez tester
test_track_id(track_id_to_test)