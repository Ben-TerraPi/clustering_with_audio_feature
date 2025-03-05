#%% Import
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

#%% DF
tracks_features = pd.read_csv(r"C:\Users\benoi\code\Ben-TerraPi\clustering_with_audio_feature\ML\tracks_features.csv")

tracks_features.info()

#%% heatmap pour corrélations

spotify_num = tracks_features.select_dtypes(include=['int64', 'float64'])

plt.figure(figsize=(12, 10))
sns.heatmap(spotify_num.corr(), annot=True, fmt=".2f", cmap='coolwarm')
plt.title("Correlation Heatmap of Spotify Song Attributes")
plt.show()

#%% preprocessing

spotify_numeric = spotify_num[["Danceability", "Energy", "Loudness", "Instrumentalness", "Valence", "Tempo"]].dropna()

scaler = RobustScaler()
spotify_scaled = pd.DataFrame(scaler.fit_transform(spotify_numeric),
                              columns=spotify_numeric.columns)
spotify_scaled

#%% valeur pour *K*

nb_clusters_to_try = np.arange(1, 21, 1)
nb_clusters_to_try

inertias = []

for k in nb_clusters_to_try:
    kmeans = KMeans(n_clusters=k, n_init='auto', random_state=42)
    kmeans.fit(spotify_scaled)
    inertias.append(kmeans.inertia_)

#%% elbow graph

fig = px.line(y=inertias,
              x=range(1, len(inertias) + 1),
              labels={'x': 'nb centroids', 'y':'Inertia'},
              title="Elbow method")
fig.show()

#%% yellow brick

kelbow_visualizer(KMeans(random_state=42),spotify_scaled , k=20)

#%% nb clusters

spotify_clusters = 8

#%% KMeans clustering

kmeans = KMeans(n_clusters=spotify_clusters, n_init='auto', random_state=42)
kmeans.fit(spotify_scaled)

#%% labels des clusters

labelling = kmeans.labels_

#%% score 

silhouette_score(spotify_scaled, labelling)

#%% 3d plot

fig_scaled = px.scatter_3d(spotify_scaled,
                           x='Danceability',
                           y='Energy',
                           z='Valence',
                           color=labelling,
                           width=500,
                           height=500)
fig_scaled.show()

#%% centroïdes des clusters

cluster_centers = kmeans.cluster_centers_

#%% DF pour les centroïdes

centroids_df = pd.DataFrame(cluster_centers, columns=spotify_scaled.columns)

#%% heatmap centroïdes

plt.figure(figsize=(12, 8))
sns.heatmap(centroids_df, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Heatmap des centroïdes des clusters (K-Means)')
plt.show()

""" # Analyse de la heatmap

Cluster 0 : "Morceaux Calmes et Peu Énergiques" - Faible danceabilité, énergie, et loudness.
Cluster 1 : "Morceaux Instrumentaux et Acoustiques" - Forte instrumentalité et acoustique modérée.
Cluster 2 : "Morceaux Équilibrés" - Caractéristiques modérées, légèrement positives en danceabilité et énergie.
Cluster 3 : "Morceaux Positifs et Énergiques" - Valence élevée, danceabilité et énergie modérées.
Cluster 4 : "Morceaux Rapides et Instrumentaux" - Tempo élevé, instrumentalité modérée.
Cluster 5 : "Morceaux Doux et Calmes" - Faible énergie, loudness, et valence.
Cluster 6 : "Morceaux Modérés" - Caractéristiques modérées, légèrement positives en danceabilité et énergie.
Cluster 7 : "Morceaux Rapides et Énergiques" - Tempo élevé, énergie modérée.

"""

#%% nb tracks par cluster

np.unique(labelling,return_counts=True)

#%% nouveau csv

tracks_features['Cluster'] = pd.Series(labelling)

tracks_features.to_csv(r"C:\Users\benoi\code\Ben-TerraPi\clustering_with_audio_feature\ML\spotify_ML_clusters.csv", index= False)

#%% export BigQuery

project_id = "discogs-random-selecta"
table_id = "discogs-random-selecta.ML.spotify_ML_clusters"

pandas_gbq.to_gbq(tracks_features, table_id , project_id)

#%% 8 playlists basé sur clusters

daily_mixes = {}

for num_cluster in np.unique(labelling):

  daily_mixes[num_cluster] = tracks_features[tracks_features['Cluster'] == num_cluster]

for key,value in daily_mixes.items():
  print("-" * 50)
  print(f"playlist {key}")
  print("-" * 50)
  display(value.sample(5)[['Title', 'Artist', "Album", "Genre", "Style"]])




