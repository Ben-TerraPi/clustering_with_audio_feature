import pandas as pd
import pandas_gbq
from IPython.display import display
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from sklearn.preprocessing import RobustScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from yellowbrick.cluster.elbow import kelbow_visualizer


spotify_df = pd.read_csv("ML/spotify_df.csv")

spotify_num = spotify_df.select_dtypes(include=['int64', 'float64'])


# heatmap to visualize correlations
plt.figure(figsize=(12, 10))
sns.heatmap(spotify_num.corr(), annot=True, fmt=".2f", cmap='coolwarm')
plt.title("Correlation Heatmap of Spotify Song Attributes")
plt.show()


# sélection des paramêtres ml
spotify_numeric = spotify_num[["Danceability", "Loudness", "Energy", "Acousticness", "Instrumentalness",	"Valence",	"Tempo"]]

"""## Preprocessing"""

scaler = RobustScaler()
spotify_scaled = pd.DataFrame(scaler.fit_transform(spotify_numeric),
                              columns=spotify_numeric.columns)
spotify_scaled

"""## Modelling with preprocessed data

## Finding the right value for *K*
"""

nb_clusters_to_try = np.arange(1, 21, 1)
nb_clusters_to_try

inertias = []

for k in nb_clusters_to_try:
    kmeans = KMeans(n_clusters=k, n_init='auto', random_state=42)
    kmeans.fit(spotify_scaled)
    inertias.append(kmeans.inertia_)

#elbow 
fig = px.line(y=inertias,
              x=range(1, len(inertias) + 1),
              labels={'x': 'nb centroids', 'y':'Inertia'},
              title="Elbow method")
fig.show()

kelbow_visualizer(KMeans(random_state=42),spotify_scaled , k=20)

"""## Creating a model with the ideal number of clusters"""

# Nombre de clusters
spotify_clusters = 8

# Appliquer K-Means clustering
kmeans = KMeans(n_clusters=spotify_clusters, n_init='auto', random_state=42)
kmeans.fit(spotify_scaled)

# Obtenir les labels des clusters
labelling = kmeans.labels_

# score silhouette
silhouette_score(spotify_scaled, labelling)

#3d plot
fig_scaled = px.scatter_3d(spotify_scaled,
                           x='Danceability',
                           y='Energy',
                           z='Valence',
                           color=labelling,
                           width=500,
                           height=500)
fig_scaled.show()

# Obtenir les centroïdes des clusters
cluster_centers = kmeans.cluster_centers_

# Créer un DataFrame pour les centroïdes
centroids_df = pd.DataFrame(cluster_centers, columns=spotify_scaled.columns)

# Tracer le heatmap des centroïdes
plt.figure(figsize=(12, 8))
sns.heatmap(centroids_df, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Heatmap des centroïdes des clusters (K-Means)')
plt.show()

"""### Noms pour les clusters

Cluster 0 : "Morceaux Calmes" - Faible danceabilité, énergie, et loudness.
Cluster 1 : "Morceaux Doux et Acoustiques" - Forte acoustique et instrumentalité, énergie modérée.
Cluster 2 : "Morceaux Équilibrés" - Caractéristiques modérées, légèrement positives en danceabilité et énergie.
Cluster 3 : "Morceaux Positifs" - Valence élevée, danceabilité et énergie modérées.
Cluster 4 : "Morceaux Instrumentaux" - Instrumentalité élevée, acoustique modérée.
Cluster 5 : "Morceaux Instrumentaux et Acoustiques" - Forte instrumentalité et acoustique modérée.
Cluster 6 : "Morceaux Acoustiques" - Forte acoustique, instrumentalité élevée.
Cluster 7 : "Morceaux Instrumentaux et Énergiques" - Forte instrumentalité, acoustique modérée, énergie et loudness modérées.

"""

# nombre de tracks par cluster
np.unique(labelling,return_counts=True)


# rajout de la colonne cluster
spotify_df['Cluster'] = pd.Series(labelling)


spotify_df.to_csv("ML/spotify_ML_clusters.csv", index= False)

"""### export to BigQuery"""

project_id = "discogs-random-selecta"
table_id = "discogs-random-selecta.ML.spotify_ML_clusters"

pandas_gbq.to_gbq(spotify_df, table_id , project_id)

"""## Generating Spotify playlists based on our clusters!"""

daily_mixes = {}

for num_cluster in np.unique(labelling):

  daily_mixes[num_cluster] = spotify_df[spotify_df['Cluster'] == num_cluster]

"""Run the cell below to print out our 8 playlists!!!"""

for key,value in daily_mixes.items():
  print("-" * 50)
  print(f"Here are some songs for playlist {key}")
  print("-" * 50)
  display(value.sample(15)[['Title', 'Artist', "Album", "Genre", "Style"]])