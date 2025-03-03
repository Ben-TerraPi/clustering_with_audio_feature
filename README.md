Continuité du projet [Discogs-Random-Selecta](https://github.com/Ben-TerraPi/Discogs-Random-Selecta)


Avec le projet ci-dessus j'ai récupéré, grâce à des requêtes API, un fichier regroupant l'intégralité des morceaux de chaque album que je possède et que j'ai répertorié sur [Discogs](https://www.discogs.com/) (une des plus grandes bases de données musicale en ligne).

Le tableau :
| album_id  | artist | album | track_id | title |
|-----------|--------|-------|----------|-------|

Le fichier : [my_tracks.csv](https://github.com/Ben-TerraPi/clustering_with_audio_feature/blob/main/my_tracks.csv) avec 5348 tracks.

Maintenant le but est de regrouper l'ensemble de ces morceaux en utilisant leurs features audio. Pour cela je vais directement récupérer celles déjà existante et créé par Spotify en utilisant son API avec [Spotipy](https://spotipy.readthedocs.io/en/2.25.1/). Peut-être qu'ulterieurement j'analyserai moi-même mes fichiers audio avec les librairies python [Librosa](https://librosa.org/doc/latest/index.html#) et [Essentia](https://essentia.upf.edu/index.html#).



