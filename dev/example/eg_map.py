from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import json
import urllib.request
mapboxt = open(".mapbox_token").read().rstrip() #my mapbox_access_token
fig = make_subplots(
    rows=1, cols=2, subplot_titles=('Map1', 'Map2'),
    specs=[[{"type": "mapbox"}, {"type": "mapbox"}]]
)

swiss_url = 'https://raw.githubusercontent.com/empet/Datasets/master/swiss-cantons.geojson'
with urllib.request.urlopen(swiss_url) as url:
    jdata = json.loads(url.read().decode())

data_url = "https://raw.githubusercontent.com/empet/Datasets/master/Swiss-synthetic-data.csv"

df = pd.read_csv(data_url)

fig.add_trace(go.Choroplethmapbox(geojson=jdata,
                                  locations=df['canton-id'],
                                  z=df['2018'],
                                  featureidkey='properties.id',
                                  colorscale='Viridis',
                                  colorbar=dict(thickness=20, x=0.46),
                                  marker=dict(opacity=0.75)), row=1, col=1)
fig.add_trace(go.Choroplethmapbox(geojson=jdata,
                                  locations=df['canton-id'],
                                  z=df['2019'],
                                  featureidkey='properties.id',
                                  colorscale='matter_r',
                                  colorbar=dict(thickness=20, x=1.02),
                                  marker=dict(opacity=0.75, line_width=0.5)), row=1, col=2);


fig.update_mapboxes(
        bearing=0,
        accesstoken=mapboxt,
        center = {"lat": 46.8181877 , "lon":8.2275124 },
 )
fig.update_layout(margin=dict(l=0, r=0, t=50, b=10));

#HERE YOU CAN CONTROL zoom
fig.update_layout(mapbox1=dict(zoom=5.9, style='carto-positron'),
                  mapbox2=dict(zoom=5.3, style='light'))

