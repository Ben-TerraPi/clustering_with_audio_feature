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

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# nettoyage

def clean_title(title):
    title = re.sub(r'["®]', '', title)  # Supprime les guillemets et les symboles de marque déposée
    title = unidecode(title)
    title = title.lower().strip()  # Convertit en minuscules et supprime les espaces superflus
    return title

def clean_album_name(album):
    album = re.sub(r'\(.*\)', '', album).strip()
    album = re.sub(r' - .*', '', album).strip()
    album = re.sub(r'[®]', '', album)  # Supprime les symboles de marque déposée
    album = album.lower().strip()  # Convertit en minuscules et supprime les espaces superflus
    return album

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# étape 1: correspondance exacte artist-titre

def get_track_id_by_artist(artist, track):
    try:
        result = sp.search(q=f'artist:{artist} track:{track}', type='track', limit=5)
        time.sleep(1)  # rate limit

        for track_info in result['tracks']['items']:
            track_name = track_info['name']
            track_artist = track_info['artists'][0]['name']

            if track_name.lower() == track.lower() and track_artist.lower() == artist.lower():
                return track_info['id']

        print(f"No exact match found for '{artist} - {track}'")
        return None
    except Exception as e:
        print(f"Erreur pour {artist} - {track}: {e}")
        return None

# étape 2: correspondance exacte titre-album

def get_track_id_by_album(track, album):
    try:
        result = sp.search(q=f'track:{track} album:{album}', type='track', limit=5)
        time.sleep(1)  # rate limit

        for track_info in result['tracks']['items']:
            track_name = track_info['name']
            track_album = track_info['album']['name']

            if track_name.lower() == track.lower() and track_album.lower() == album.lower():
                return track_info['id']

        print(f"No exact match found for '{track} - {album}'")
        return None
    except Exception as e:
        print(f"Erreur pour {track} - {album}: {e}")
        return None
    
# étape 3: Correspondance exacte artiste-titre-album

def get_track_id_by_artist_album(artist, track, album):
    try:
        result = sp.search(q=f'artist:{artist} track:{track} album:{album}', type='track', limit=5)
        time.sleep(1)  # rate limit

        for track_info in result['tracks']['items']:
            track_name = track_info['name']
            track_artist = track_info['artists'][0]['name']
            track_album = track_info['album']['name']

            if (track_name.lower() == track.lower() and
                track_artist.lower() == artist.lower() and
                track_album.lower() == album.lower()):
                return track_info['id']

        print(f"No exact match found for '{artist} - {track} - {album}'")
        return None
    except Exception as e:
        print(f"Erreur pour {artist} - {track} - {album}: {e}")
        return None

# étape 4: fuzzy match artiste-titre-album

def get_track_id_fuzzy(artist, track, album):
    try:
        result = sp.search(q=f'artist:{artist} track:{track} album:{album}', type='track', limit=10)
        time.sleep(1)  # rate limit

        best_match = None
        best_score = 0

        for track_info in result['tracks']['items']:
            track_name = track_info['name']
            track_artist = track_info['artists'][0]['name']
            track_album = track_info['album']['name']

            name_score = fuzz.ratio(track.lower(), track_name.lower())
            artist_score = fuzz.ratio(artist.lower(), track_artist.lower())
            album_score = fuzz.ratio(album.lower(), track_album.lower())

            avg_score = (name_score + artist_score + album_score) / 3

            if avg_score > best_score:
                best_score = avg_score
                best_match = track_info

        if best_match and best_score >= 70:
            print(f"Fuzzy match found for '{artist} - {track} - {album}' with score {best_score}")
            return best_match['id']

        print(f"No fuzzy match found for '{artist} - {track} - {album}'")
        return None
    except Exception as e:
        print(f"Erreur pour {artist} - {track} - {album}: {e}")
        return None

# étape 5: fuzzy match titre-album

def get_track_id_fuzzy_track_album(track, album):
    try:
        result = sp.search(q=f'track:{track} album:{album}', type='track', limit=10)
        time.sleep(1)  # rate limit

        best_match = None
        best_score = 0

        for track_info in result['tracks']['items']:
            track_name = track_info['name']
            track_album = track_info['album']['name']

            name_score = fuzz.ratio(track.lower(), track_name.lower())
            album_score = fuzz.ratio(album.lower(), track_album.lower())

            avg_score = (name_score + album_score) / 2

            if avg_score > best_score:
                best_score = avg_score
                best_match = track_info

        if best_match and best_score >= 70:
            print(f"Fuzzy match found for '{track} - {album}' with score {best_score}")
            return best_match['id']

        print(f"No fuzzy match found for '{track} - {album}'")
        return None
    except Exception as e:
        print(f"Erreur pour {track} - {album}: {e}")
        return None

# étape 6: fuzzy match artiste-titre

def get_track_id_fuzzy_artist_track(artist, track):
    try:
        result = sp.search(q=f'artist:{artist} track:{track}', type='track', limit=10)
        time.sleep(1)  # rate limit

        best_match = None
        best_score = 0

        for track_info in result['tracks']['items']:
            track_name = track_info['name']
            track_artist = track_info['artists'][0]['name']

            name_score = fuzz.ratio(track.lower(), track_name.lower())
            artist_score = fuzz.ratio(artist.lower(), track_artist.lower())

            avg_score = (name_score + artist_score) / 2

            if avg_score > best_score:
                best_score = avg_score
                best_match = track_info

        if best_match and best_score >= 70:
            print(f"Fuzzy match found for '{artist} - {track}' with score {best_score}")
            return best_match['id']

        print(f"No fuzzy match found for '{artist} - {track}'")
        return None
    except Exception as e:
        print(f"Erreur pour {artist} - {track}: {e}")
        return None
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def get_track_id(artist, track, album):
    artist = clean_title(artist)
    track = clean_title(track)
    album = clean_album_name(album)
    track_id = get_track_id_by_artist(artist, track)
    if track_id:
        return track_id
    track_id = get_track_id_by_album(track, album)
    if track_id:
        return track_id
    track_id = get_track_id_by_artist_album(artist, track, album)
    if track_id:
        return track_id
    track_id = get_track_id_fuzzy(artist, track, album)
    if track_id:
        return track_id
    track_id = get_track_id_fuzzy_track_album(track, album)
    if track_id:
        return track_id
    return get_track_id_fuzzy_artist_track(artist, track)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#création nouveau csv

def add_id_to_csv(input_file_path, output_file_path, limit=None):
    df = pd.read_csv(input_file_path)
    print("Récupération des spotify_id")

    # limite pour test
    if limit:
        df = df.head(limit)

    # ajout colonne ID + barre de progression
    tqdm.pandas()
    df['spotify_id'] = df.progress_apply(lambda row: get_track_id(row['artist'], row['title'], row['album']), axis=1)

    # sauvegarde nouveau csv
    df.to_csv(output_file_path, index=False)

    print(f"Les IDs Spotify ont été ajoutés et sauvegardés dans {output_file_path}")


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# code de départ

# def get_title_artist_id(artist, track):
#     try:
#         result = sp.search(q=f'artist:{artist} track:{track}', type='track', limit=1)
#         time.sleep(1)  # rate limit

#         if result['tracks']['items']:
#             return result['tracks']['items'][0]['id']
#         else:
#             return None
#     except Exception as e:
#         print(f"Erreur pour {artist} - {track}: {e}")
#         return None

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# test fonction

# add_id_to_csv('my_tracks.csv', 'spotify/my_tracks_spotify_ids_test.csv', limit=100)

# #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


add_id_to_csv('my_tracks.csv', 'spotify/my_tracks_spotify_id.csv')

# my_tracks_spotify_id = pd.read_csv("spotify/my_tracks_spotify_id.csv")

# #ID unique
# my_tracks_with_spotify_id  = my_tracks_spotify_id[my_tracks_spotify_id['spotify_id'].notnull()].drop_duplicates(subset='spotify_id').to_csv("spotify/my_tracks_with_spotify_id.csv")
