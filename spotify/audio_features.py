#               !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#       .audio_features bloqué par Spotify depuis novembre 2024
#               !!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time

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

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

df = pd.read_csv('spotify/my_tracks_spotify_id.csv')

df_with_id = df[df['spotify_id'].notna()].copy()

# Liste des colonnes des audio features
audio_features_columns = [
    "danceability", "energy", "key", "loudness", "mode", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo"
]

for col in audio_features_columns:
    df_with_id[col] = None

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<

def get_audio_features(track_id):
    try:
        features = sp.audio_features(track_id)[0]
        time.sleep(1)  # rate limit
        
        if features:
            return {col: features.get(col, None) for col in audio_features_columns}
        else:
            return {col: None for col in audio_features_columns}
    except Exception as e:
        print(f"erreur pour {track_id}: {e}")
        return {col: None for col in audio_features_columns}

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

print(f"audio features pour {len(df_with_id)} morceaux...")

for index, row in df_with_id.iterrows():
    features = get_audio_features(row['spotify_id'])
    for col in audio_features_columns:
        df_with_id.at[index, col] = features[col]

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

df_with_id.to_csv('spotify/my_tracks_audio_features.csv', index=False)


print("ok")


sp.audio_features("2h5PrGmfG1kDuoYPkfuLzn")

