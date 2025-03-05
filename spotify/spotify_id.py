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
    # title = re.sub(r'\(.*\)', '', title).strip()  # parenthèses
    # title = re.sub(r'["]', '', title)  # guillemets
    title = unidecode(title)  # caractères accentués
    # title = re.sub(r'[^a-zA-Z0-9\s()-]', '', title)  # caractères spéciaux
    # title = re.sub(r"n'", "ng", title)
    # title = re.sub(r'\s+', ' ', title).strip()  # espaces
    return title

def clean_album_name(album):
    album = re.sub(r'\(.*\)', '', album).strip()  # parenthèses
    # album = re.sub(r' - .*', '', album).strip()  # tiret
    album = unidecode(album)  # caractères accentués
    # album = re.sub(r'[^a-zA-Z0-9\s()-]', '', album) # caractères spéciaux
    # album = re.sub(r'\s+', ' ', album).strip()  # espaces
    return album 

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# recherche Spotify

def search_spotify(query, search_type='track', limit=10):
    try:
        result = sp.search(q=query, type=search_type, limit=limit)
        time.sleep(1)  # rate limit
        return result
    except Exception as e:
        print(f"Erreur lors de la recherche Spotify: {e}")
        return None
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><

# étape 1: correspondance exacte artiste-titre
def get_track_id_by_artist(artist, track):
    try:
        # Nettoyage des titres
        track = clean_title(track)
        artist = clean_title(artist)

        # Recherche avec l'artiste et le titre
        result = sp.search(q=f'artist:{artist} track:{track}', type='track', limit=10)
        time.sleep(1)  # rate limit

        # Correspondance exacte titre-artiste
        for track_info in result['tracks']['items']:
            track_name = clean_title(track_info['name'])
            track_artist = clean_title(track_info['artists'][0]['name'])

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
        # Nettoyage des titres
        track = clean_title(track)
        album = clean_title(album)

        # Recherche avec le titre et l'album
        result = sp.search(q=f'track:{track} album:{album}', type='track', limit=10)
        time.sleep(1)  # rate limit

        # Correspondance exacte titre-album
        for track_info in result['tracks']['items']:
            track_name = clean_title(track_info['name'])
            track_album = clean_title(track_info['album']['name'])

            if track_name.lower() == track.lower() and track_album.lower() == album.lower():
                return track_info['id']

        print(f"No exact match found for '{track} - {album}'")
        return None
    except Exception as e:
        print(f"Erreur pour {track} - {album}: {e}")
        return None

# étape 3: correspondance exacte artiste-titre-album
def get_track_id_by_artist_album(artist, track, album):
    try:
        # Nettoyage des titres
        track = clean_title(track)
        artist = clean_title(artist)
        album = clean_title(album)

        # Recherche avec l'artiste, le titre et l'album
        result = sp.search(q=f'artist:{artist} track:{track} album:{album}', type='track', limit=10)
        time.sleep(1)  # rate limit

        # Correspondance exacte artiste-titre-album
        for track_info in result['tracks']['items']:
            track_name = clean_title(track_info['name'])
            track_artist = clean_title(track_info['artists'][0]['name'])
            track_album = clean_title(track_info['album']['name'])

            if (track_name.lower() == track.lower() and
                track_artist.lower() == artist.lower() and
                track_album.lower() == album.lower()):
                return track_info['id']

        print(f"No exact match found for '{artist} - {track} - {album}'")
        return None
    except Exception as e:
        print(f"Erreur pour {artist} - {track} - {album}: {e}")
        return None

# étape 4: correspondance approximative artiste-titre-album
def get_track_id_fuzzy(artist, track, album):
    try:
        # Nettoyage des titres
        track = clean_title(track)
        artist = clean_title(artist)
        album = clean_album_name(album)

        # Recherche avec l'artiste, le titre et l'album
        result = sp.search(q=f'artist:{artist} track:{track} album:{album}', type='track', limit=10)
        time.sleep(1)  # rate limit

        # Recherche de correspondance approximative
        best_match = None
        best_score = 0

        for track_info in result['tracks']['items']:
            track_name = clean_title(track_info['name'])
            track_artist = clean_title(track_info['artists'][0]['name'])
            track_album = clean_album_name(track_info['album']['name'])

            # Calcul du score de similarité
            score = fuzz.ratio(f"{track} {artist} {album}", f"{track_name} {track_artist} {track_album}")

            if score > best_score:
                best_score = score
                best_match = track_info

        if best_match and best_score >= 80:  # Seuil de similarité
            print(f"Approximate match found for '{artist} - {track} - {album}' with score {best_score}")
            return best_match['id']

        print(f"No approximate match found for '{artist} - {track} - {album}'")
        return None
    except Exception as e:
        print(f"Erreur pour {artist} - {track} - {album}: {e}")
        return None

# étape 5: correspondance approximative titre-album
def get_track_id_fuzzy_track_album(track, album):
    try:
        # Nettoyage des titres
        track = clean_title(track)
        album = clean_album_name(album)

        # Recherche avec le titre et l'album
        result = sp.search(q=f'track:{track} album:{album}', type='track', limit=10)
        time.sleep(1)  # rate limit

        # Recherche de correspondance approximative
        best_match = None
        best_score = 0

        for track_info in result['tracks']['items']:
            track_name = clean_title(track_info['name'])
            track_album = clean_album_name(track_info['album']['name'])

            # Calcul du score de similarité
            score = fuzz.ratio(f"{track} {album}", f"{track_name} {track_album}")

            if score > best_score:
                best_score = score
                best_match = track_info

        if best_match and best_score >= 80:  # Seuil de similarité
            print(f"Approximate match found for '{track} - {album}' with score {best_score}")
            return best_match['id']

        print(f"No approximate match found for '{track} - {album}'")
        return None
    except Exception as e:
        print(f"Erreur pour {track} - {album}: {e}")
        return None

# étape 6: correspondance approximative artiste-titre
def get_track_id_fuzzy_artist_track(artist, track):
    try:
        # Nettoyage des titres
        track = clean_title(track)
        artist = clean_title(artist)

        # Recherche avec l'artiste et le titre
        result = sp.search(q=f'artist:{artist} track:{track}', type='track', limit=10)
        time.sleep(1)  # rate limit

        # Recherche de correspondance approximative
        best_match = None
        best_score = 0

        for track_info in result['tracks']['items']:
            track_name = clean_title(track_info['name'])
            track_artist = clean_title(track_info['artists'][0]['name'])

            # Calcul du score de similarité
            score = fuzz.ratio(f"{track} {artist}", f"{track_name} {track_artist}")

            if score > best_score:
                best_score = score
                best_match = track_info

        if best_match and best_score >= 80:  # Seuil de similarité
            print(f"Approximate match found for '{artist} - {track}' with score {best_score}")
            return best_match['id']

        print(f"No approximate match found for '{artist} - {track}'")
        return None
    except Exception as e:
        print(f"Erreur pour {artist} - {track}: {e}")
        return None
    
# étape 7 : code de départ (au cas où...)
def clean(title):
    title = re.sub(r'\(.*\)', '', title).strip()  # Supprime le contenu entre parenthèses
    title = unidecode(title)  # Convertit les caractères accentués
    return title

def get_title_artist_id(artist, track):
    track = clean(track)
    try:
        result = sp.search(q=f'artist:{artist} track:{track}', type='track', limit=10)
        time.sleep(1)  # rate limit

        if result['tracks']['items']:
            track_info = result['tracks']['items'][0]
            track_name = clean(track_info['name'])
            track_artist = clean(track_info['artists'][0]['name'])

            # Vérifiez que les deux correspondent
            if track_name.lower() == track.lower() and track_artist.lower() == artist.lower():
                print(f"Match found for '{artist} - {track}'")
                return track_info['id']
            else:
                print(f"Partial match found for '{artist} - {track}', but not exact.")
        else:
            print(f"No match found for '{artist} - {track}'")
    except Exception as e:
        print(f"Erreur pour {artist} - {track}: {e}")
        return None

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><

# obtenir l'ID spotify

def get_track_id(artist, track, album):
    # album = clean_album_name(album)
    # track = clean_title(track)
    # artist = clean_title(artist)

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
    track_id = get_track_id_fuzzy_artist_track(artist, track)
    if track_id:
        return track_id
    return get_title_artist_id(artist, track)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# création csv
def add_id_to_csv(input_file_path, output_file_path, limit=None):
    df = pd.read_csv(input_file_path)
    print("Récupération des spotify_id")

    if limit:
        df = df.head(limit)

    tqdm.pandas()
    df['spotify_id'] = df.progress_apply(lambda row: get_track_id(row['artist'], row['title'], row['album']), axis=1)

    df.to_csv(output_file_path, index=False)
    print(f"Les IDs Spotify ont été ajoutés et sauvegardés dans {output_file_path}")


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# test fonction

# add_id_to_csv('my_tracks.csv', 'spotify/my_tracks_spotify_ids_test.csv', limit=200)

# #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


add_id_to_csv('my_tracks.csv', 'spotify/my_tracks_spotify_id.csv')

my_tracks_spotify_id = pd.read_csv("spotify/my_tracks_spotify_id.csv")

#ID unique
my_tracks_with_spotify_id  = my_tracks_spotify_id[my_tracks_spotify_id['spotify_id'].notnull()]
my_tracks_with_spotify_id.drop_duplicates(subset='spotify_id').to_csv("spotify/my_tracks_with_spotify_id.csv")

#No ID
my_tracks_without_spotify_id = my_tracks_spotify_id[my_tracks_spotify_id['spotify_id'].isnull()]
my_tracks_without_spotify_id.to_csv("spotify/my_tracks_without_spotify_id.csv")