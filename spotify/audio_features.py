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

# Authentification via client_credentials
client_credentials_manager = SpotifyClientCredentials(client_id = SPOTIPY_CLIENT_ID, client_secret = SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

# 🔄 Test de l'authentification
try:
    token = sp.auth_manager.get_access_token(as_dict=False)
    print(f"✅ Authentification réussie ! Token : {token[:20]}...")  # Afficher les 20 premiers caractères du token
except Exception as e:
    print(f"❌ Erreur d'authentification : {e}")

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>DataFrame

# Charger le fichier avec les IDs Spotify
df = pd.read_csv('spotify/my_tracks_spotify_ids.csv')

df_with_id = df[df['spotify_id'].notna()].copy()  # Avec ID
df_without_id = df[df['spotify_id'].isna()].copy()  # Sans ID

# Liste des colonnes des audio features
audio_features_columns = [
    "danceability", "energy", "key", "loudness", "mode", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo"
]

# Initialiser les nouvelles colonnes à None
for col in audio_features_columns:
    df_with_id[col] = None

# Fonction pour récupérer les audio features
def get_audio_features(track_id):
    try:
        features = sp.audio_features(track_id)[0]  # Récupère les features du morceau
        time.sleep(0.5)  # Pause pour éviter le rate limit
        
        if features:
            return {col: features.get(col, None) for col in audio_features_columns}
        else:
            return {col: None for col in audio_features_columns}
    except Exception as e:
        print(f"❌ Erreur pour {track_id}: {e}")
        return {col: None for col in audio_features_columns}

# Appliquer la fonction uniquement aux morceaux avec un ID
print(f"🔄 Récupération des audio features pour {len(df_with_id)} morceaux...")

for index, row in df_with_id.iterrows():
    features = get_audio_features(row['spotify_id'])
    for col in audio_features_columns:
        df_with_id.at[index, col] = features[col]

# Fusionner les morceaux avec et sans ID pour garder la liste complète
df_final = pd.concat([df_with_id, df_without_id], ignore_index=True)

# Sauvegarde des fichiers
df_final.to_csv('fichier_audio_features.csv', index=False)
df_without_id.to_csv('morceaux_sans_id.csv', index=False)  # Liste des morceaux non trouvés

print(f"✅ Terminé !")
print(f"📁 Fichier complet avec audio features : 'fichier_audio_features.csv'")
print(f"⚠️ {len(df_without_id)} morceaux introuvables enregistrés dans 'morceaux_sans_id.csv'")

sp.audio_features("2h5PrGmfG1kDuoYPkfuLzn")

