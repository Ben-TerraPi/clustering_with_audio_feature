import os
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/discogs-random-selecta-c158979d33c1.json"

client = bigquery.Client()

query1 = """
    SELECT *
    FROM `discogs-random-selecta.my_data.my_tracks`
"""

query2 = """
    SELECT *
    FROM `discogs-random-selecta.my_data.tracks_features`
"""

client.query(query1).to_dataframe().to_csv('my_tracks.csv', index = False)

client.query(query2).to_dataframe().to_csv("ML/tracks_features.csv", index = False)

print("datasets importés")

