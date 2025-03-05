from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from tqdm import tqdm

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = "http://localhost:8080/callback"

# Authentification

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = SPOTIPY_CLIENT_ID,
                                               client_secret = SPOTIPY_CLIENT_SECRET,
                                               redirect_uri = SPOTIPY_REDIRECT_URI,
                                               scope='playlist-modify-public'))

# Test authentification
try:
    token = sp.auth_manager.get_access_token(as_dict=False)
    print(f"✅ Authentification réussie !")
except Exception as e:
    print(f"❌ Erreur d'authentification : {e}")

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def create_spotify_playlist(csv_file_path, sp, playlist_name, cluster=None):

    df = pd.read_csv(csv_file_path)

    # après ML
    if cluster is not None:
        df = df[df['Cluster'] == cluster]

    track_ids = df['spotify_id'].tolist()

    # créer playlist
    user_id = sp.me()['id']
    playlist = sp.user_playlist_create(user_id, name = playlist_name, public=True)
    playlist_id = playlist['id']

    for i in tqdm(range(0, len(track_ids), 100), desc="morceaux >> playlist"):
        sp.playlist_add_items(playlist_id, track_ids[i:i+100])

    print(f"créée avec succès : {playlist['external_urls']['spotify']}")

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FICHIER avec spotify ID

create_spotify_playlist("spotify/my_tracks_with_spotify_id.csv", sp, 'Ma nouvelle playlist')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> export playlist ML_Cluster

# create_spotify_playlist("ML/spotify_ML_clusters.csv", sp, "Calmes", cluster = 0)
# create_spotify_playlist("ML/spotify_ML_clusters.csv", sp, "Instrumentaux", cluster = 1)
# create_spotify_playlist("ML/spotify_ML_clusters.csv", sp, "Équilibrés", cluster = 2)
# create_spotify_playlist("ML/spotify_ML_clusters.csv", sp, "Positifs et Énergiques", cluster = 3)
# create_spotify_playlist("ML/spotify_ML_clusters.csv", sp, "Rapides et Instrumentaux", cluster = 4)
# create_spotify_playlist("ML/spotify_ML_clusters.csv", sp, "Doux et Calmes", cluster = 5)
# create_spotify_playlist("ML/spotify_ML_clusters.csv", sp, "Modérés", cluster = 6)
# create_spotify_playlist("ML/spotify_ML_clusters.csv", sp, "Rapides et Énergiques", cluster = 7)

