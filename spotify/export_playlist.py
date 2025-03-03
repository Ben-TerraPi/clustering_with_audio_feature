from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import csv
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


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FONCTION POUR EXPORT PLAYLIST

def create_spotify_playlist(csv_file_path, sp, playlist_name, cluster=None):

    df = pd.read_csv(csv_file_path)

    # Filtrer par cluster si spécifié
    if cluster is not None:
        df = df[df['Cluster'] == cluster]

    track_ids = df['spotify_id'].tolist()

    # Créer une playlist
    user_id = sp.me()['id']
    playlist = sp.user_playlist_create(user_id, name = playlist_name, public=True)
    playlist_id = playlist['id']

    # Ajouter des morceaux à la playlist
    # lots de 100 pour éviter les limitations de l'API
    for i in tqdm(range(0, len(track_ids), 100), desc="Ajout des morceaux à la playlist"):
        sp.playlist_add_items(playlist_id, track_ids[i:i+100])

    print(f"Playlist créée avec succès : {playlist['external_urls']['spotify']}")


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FICHIER avec spotify ID

create_spotify_playlist("spotify/my_tracks_with_spotify_id.csv", sp, 'Ma nouvelle playlist')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> export playlist ML_Cluster

# create_spotify_playlist("ML/spotify_ML_clusters.csv", sp, "Calmes", cluster = 0)
# create_spotify_playlist("ML/spotify_ML_clusters.csv", sp, "Doux et Acoustiques", cluster = 1)
# create_spotify_playlist("ML/spotify_ML_clusters.csv", sp, "Équilibrés", cluster = 2)
# create_spotify_playlist("ML/spotify_ML_clusters.csv", sp, "Positifs", cluster = 3)
# create_spotify_playlist("ML/spotify_ML_clusters.csv", sp, "Instrumentaux", cluster = 4)
# create_spotify_playlist("ML/spotify_ML_clusters.csv", sp, "Instrumentaux et Acoustiques", cluster = 5)
# create_spotify_playlist("ML/spotify_ML_clusters.csv", sp, "Acoustiques", cluster = 6)
# create_spotify_playlist("ML/spotify_ML_clusters.csv", sp, "Instrumentaux et Énergiques", cluster = 7)
