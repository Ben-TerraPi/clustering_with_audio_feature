import pandas as pd
import pandas_gbq


my_tracks_spotify_id = pd.read_csv("spotify/my_tracks_spotify_ids.csv")

my_tracks_with_spotify_id  = pd.read_csv("spotify/my_tracks_with_spotify_id.csv")

# export GBQ

project_id = "discogs-random-selecta"

dfs = [my_tracks_spotify_id,
       my_tracks_with_spotify_id,
       my_tracks_without_spotify_id
       ]

def get_var_name(var):
    for name, value in globals().items():
        if value is var:
            return name

for df in dfs:
  table_id = f"discogs-random-selecta.my_data.{get_var_name(df)}"
  pandas_gbq.to_gbq(df, table_id, project_id)
  
print("tableaux exportés")

