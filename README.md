### !...Read me en cours de documentation...!

Continuité du projet [Discogs-Random-Selecta](https://github.com/Ben-TerraPi/Discogs-Random-Selecta)


Avec le projet ci-dessus j'ai récupéré, grâce à des requêtes API, un fichier regroupant l'intégralité des morceaux de chaque album que je possède et que j'ai répertorié sur [Discogs](https://www.discogs.com/) (une des plus grandes bases de données musicale en ligne).

Le tableau :
| album_id  | artist | album | track_id | title |
|-----------|--------|-------|----------|-------|

Le fichier : [my_tracks.csv](https://github.com/Ben-TerraPi/clustering_with_audio_feature/blob/main/my_tracks.csv) avec 5348 tracks.

Maintenant le but est de regrouper l'ensemble de ces morceaux en utilisant leurs features audio. Pour cela je vais directement récupérer celles déjà existante et créé par Spotify en utilisant son API avec [Spotipy](https://spotipy.readthedocs.io/en/2.25.1/). Peut-être qu'ulterieurement j'analyserai moi-même mes fichiers audio avec les librairies python [Librosa](https://librosa.org/doc/latest/index.html#) et [Essentia](https://essentia.upf.edu/index.html#).

# Dossier [Spotify](https://github.com/Ben-TerraPi/clustering_with_audio_feature/tree/main/spotify)

## [spotify_id](https://github.com/Ben-TerraPi/clustering_with_audio_feature/blob/main/spotify/spotify_id.py)

Après activation de mes credentials développeur Spotify pour l'authentification via l'API il est nécessaire dans un premier temps de requêter la base de donnée pour recouper mon tableau avec les titres disponibles afin de récuperer les ID de chaque titres en utilisant le nom de l'artiste et le tire du morceau avec ces fonctions:

```
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
```
Un nouveau fichier [my_tracks_spotify_ids.csv](https://github.com/Ben-TerraPi/clustering_with_audio_feature/blob/main/spotify/my_tracks_spotify_ids.csv) est créé. Sur les 5348 morceaux j'ai 4366 résultats. Les 982 titres manquants ne sont pas disponibles sur Spotify.

## [audio_features.py](https://github.com/Ben-TerraPi/clustering_with_audio_feature/blob/main/spotify/audio_features.py)

Je suis resté bloqué sur cette étape avant de comprendre que Spotify avait fait le choix de bloqué l'attribut .audio_features depuis le mois de Novembre 2024 ne permettant plus de récupérer les données correspondantes.
N.B. Je garde mon code dans le cas d'un retour de la fonctionnalité.

## Alternative pour récupération des features audio avec le site [Exportify]([https://www.chosic.com/spotify-playlist-sorter/](https://exportify.net/))

Malgré la fermeture de l'accès par Spotify à certaine fonctionnalité de l'API il existe encore des sites qui fournissent les données souhaités. Pour cela il est nécessaire de créer une playlist Spotify afin de pouvoir l'exporté vers le site en question.

### [export_playlist.py](https://github.com/Ben-TerraPi/clustering_with_audio_feature/blob/main/spotify/export_playlist.py)

Fonction pour l'exportation de mes morceaux vers spotify grâce à leur ID:

```
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
```

Avec ``` create_spotify_playlist("spotify/my_tracks_spotify_ids.csv", sp, 'Ma nouvelle playlist') ``` ma [playlist](https://open.spotify.com/playlist/7nFejU5iwTVpYQUfFM1G4E) est accessible et téléchargeable via Exportify avec les données 




