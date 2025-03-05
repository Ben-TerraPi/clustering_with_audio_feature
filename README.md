### !...Read me en cours de documentation...!

Continuité du projet [Discogs-Random-Selecta](https://github.com/Ben-TerraPi/Discogs-Random-Selecta)


Avec le projet ci-dessus, j'ai récupéré, grâce à des requêtes API, un fichier regroupant l'intégralité des morceaux de chaque album que je possède et que j'ai répertorié sur [Discogs](https://www.discogs.com/) (l'une des plus grandes bases de données musicales en ligne).

Le tableau :
| album_id  | artist | album | track_id | title | 
|-----------|--------|-------|----------|-------|

Le fichier : [my_tracks.csv](https://github.com/Ben-TerraPi/Discogs-Random-Selecta/blob/main/my_tracks.csv) avec **5347** tracks.

Maintenant, le but est de regrouper l'ensemble de ces morceaux en utilisant leurs caractéristiques audio. Pour cela, je vais directement récupérer celles déjà existantes et créées par Spotify en utilisant son API avec [Spotipy](https://spotipy.readthedocs.io/en/2.25.1/). Peut-être qu'ultérieurement, j'analyserai moi-même mes fichiers audio dans un autre projet avec les bibliothèques Python [Librosa](https://librosa.org/doc/latest/index.html#) et [Essentia](https://essentia.upf.edu/index.html#).

# Dossier [Spotify](https://github.com/Ben-TerraPi/clustering_with_audio_feature/tree/main/spotify)

## Fichier [spotify_id.py](https://github.com/Ben-TerraPi/clustering_with_audio_feature/blob/main/spotify/spotify_id.py)

Après l'activation de mes identifiants développeur Spotify pour l'authentification via l'API, il est nécessaire dans un premier temps de requêter la base de données pour recouper mon tableau avec les titres disponibles afin de récupérer les ID de chaque titre en utilisant le nom de l'artiste, le titre et l'album du morceau.

À la suite de mes tests, je réalise qu'il faut rechercher des correspondances en plusieurs étapes pour s'assurer de la qualité des données.

- nettoyage
- étape 1: correspondance exacte artist-titre
- étape 2: correspondance exacte titre-album
- étape 3: Correspondance exacte artiste-titre-album
- étape 4: fuzzy match artiste-titre-album
- étape 5: fuzzy match titre-album
- étape 6: fuzzy match artiste-titre
- étape 7: code de départ moins précis qui récupère seulement si artiste "AND" titre sont présent (au cas où..)

7 fonctions regroupées dans une:

```
def get_track_id(artist, track, album):

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
```

Cette dernière est appelé lors de la création du nouveau tableau [my_tracks_spotify_id.csv](https://github.com/Ben-TerraPi/clustering_with_audio_feature/blob/main/spotify/my_tracks_spotify_id.csv):

```
def add_id_to_csv(input_file_path, output_file_path, limit=None):
    df = pd.read_csv(input_file_path)
    print("Récupération des spotify_id")

    if limit:
        df = df.head(limit)

    tqdm.pandas()
    df['spotify_id'] = df.progress_apply(lambda row: get_track_id(row['artist'], row['title'], row['album']), axis=1)

    df.to_csv(output_file_path, index=False)
    print(f"Les IDs Spotify ont été ajoutés et sauvegardés dans {output_file_path}")
```

Sur les 5347 morceaux:
- **4113** spotify_id unique récupéré: [my_tracks_with_spotify_id.csv](https://github.com/Ben-TerraPi/clustering_with_audio_feature/blob/main/spotify/my_tracks_with_spotify_id.csv)
- 149 doublons
- 1085 morceaux non identifié: [my_tracks_without_spotify_id.csv](https://github.com/Ben-TerraPi/clustering_with_audio_feature/blob/main/spotify/my_tracks_without_spotify_id.csv)
(ils représentent pour un pourcentage élevé les titres venant de compilations où le nom de l'artiste est appelé "Various")


## Fichier [audio_features.py](https://github.com/Ben-TerraPi/clustering_with_audio_feature/blob/main/spotify/audio_features.py)

Je suis resté bloqué sur cette étape avant de comprendre que Spotify avait fait le choix de bloquer l'attribut **.audio_features** (erreur 403) depuis le mois de novembre 2024, ne permettant plus de récupérer les données correspondantes. 
N.B. : Je garde mon code dans le cas d'un retour de la fonctionnalité.

### Alternative pour récupération des features audio avec le site [Exportify](https://exportify.net/)

Malgré la fermeture de l'accès par Spotify à certaines fonctionnalités de l'API, il existe encore des sites qui fournissent les données souhaitées. Pour cela, il est nécessaire de créer une playlist Spotify afin de pouvoir l'exporter vers le site en question.

## Fichier [export_playlist.py](https://github.com/Ben-TerraPi/clustering_with_audio_feature/blob/main/spotify/export_playlist.py)

Fonction pour l'exportation de mes morceaux vers spotify grâce à leur ID:

```
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
```

Avec `create_spotify_playlist("spotify/my_tracks_spotify_ids.csv", sp, 'Ma nouvelle playlist')` ma [playlist](https://open.spotify.com/playlist/3XjEseEzqCk5wmensDKdfd) est accessible et téléchargeable en **.csv** via **Exportify** pour récupérer les caractéristiques audio des morceaux.

# Etape de travail BigQuery

Une fois le fichier récupéré j'utilise un de mes projets sur BigQuery pour les prochaines étapes:

- vérification de clé primaire
- merge de différent tableau
- mise forme du tableau final

Pour rappel mon premier tableau ressemble à cela après récupération des ID spotify:
| album_id  | artist | album | track_id | title |spotify_id |
|-----------|--------|-------|----------|-------|-----------|

## Primary key
```
#TEST PRIMARY KEY
SELECT
spotify_id, #track_id
COUNT(*) AS nb
FROM `my_data.my_tracks_with_spotify_id`
GROUP BY
spotify_id #track_id
HAVING nb>=2
ORDER BY nb DESC
```
**spotify_id** et **track_id** représente bien des valeurs uniques chacune.

## Left join

Je récupère les infos de **genre** et **style** avec à un autre tableau:
```
SELECT m.spotify_id,
m.album,
m.artist,
m.track_id,
m.title,
c.genre,
c.style
FROM discogs-random-selecta.my_data.my_tracks_with_spotify_id as m
LEFT JOIN discogs-random-selecta.my_data.collection_clean as c
ON m.album_id = c.id
```

| spotify_id | album | artist | track_id | title | genre | style |
|------------|-------|--------|----------|-------|-------|-------|

Ensuite y ajoute mes données **Exportify** avec une vue intermédiaire avant création de la table final

```
#CREATION final_v1
SELECT
g.*,
l.* EXCEPT(track_id)
FROM `my_data.left_join_genre_id`as g
LEFT JOIN discogs-random-selecta.export_spotify.4113_join as l
ON g.spotify_id = l.Track_Id
```

Après avoir renommé et selectioné l'ordre des colonnes mon tableau ressemble à cela:

| Track_id | Artist | Title |Album | Genre | Style | Popularity | Danceability | Energy | Loudness | Speechiness | Acousticness | Instrumentalness | Liveness | Valence | Tempo | Time_Signature | Time | Key | Camelot | Spotify_key| Spotify_mode | spotify_id |
|----------|--------|-------|------|-------|-------|------------|--------------|--------|----------|-------------|--------------|------------------|----------|---------|-------|----------------|------|-----|---------|------------|--------------|------------|

# Dossier [ML](https://github.com/Ben-TerraPi/clustering_with_audio_feature/tree/main/ML)

## Fichier [tracks_features.csv](https://github.com/Ben-TerraPi/clustering_with_audio_feature/blob/main/ML/tracks_features.csv)

Tableau final importé depuis **BigQuery**
Pour information la signification des caractéristiques audio récupérés sont toujours visible sur le [site développeur Spotify](https://developer.spotify.com/documentation/web-api/reference/get-audio-features)



