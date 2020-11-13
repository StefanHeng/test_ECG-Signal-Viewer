import json
import logging
import os

import dash
from dash.dependencies import Input, Output, State

import dash_core_components as dcc

import dash_html_components as html

import dash_table

from flask_caching import Cache

import numpy as np

import plotly.express as px
import plotly.graph_objs as go

import vaex

geo_filename = 'example/taxi_zones-tiny.json'
with open(geo_filename) as f:
    geo_json = json.load(f)
zone_filename = 'example/zone.json'
with open(zone_filename) as f:
    zmapper = json.load(f)
zone_index_to_name = {int(index): name for index, name in zmapper.items()}


def create_figure_geomap(pickup_counts, zone, zoom=10, center={"lat": 40.7, "lon": -73.99}):
    geomap_data = {
        'count': pickup_counts,
        'log_count': np.log10(pickup_counts),
        'zone_name': list(zmapper.values())
    }

    fig = px.choropleth_mapbox(geomap_data,
                               geojson=geo_json,
                               color="log_count",
                               locations="zone_name",
                               featureidkey="properties.zone",
                               mapbox_style="carto-positron",
                               hover_data=['count'],
                               zoom=zoom,
                               center=center,
                               opacity=0.5,
                               )
    # Custom tool-tip
    hovertemplate = '<br>Zone: %{location}' \
                    '<br>Number of trips: %{customdata:.3s}'
    fig.data[0]['hovertemplate'] = hovertemplate

    # draw the selected zone
    geo_json_selected = geo_json.copy()
    geo_json_selected['features'] = [
        feature for feature in geo_json_selected['features'] if feature['properties']['zone'] == zone_index_to_name[zone]
    ]

    geomap_data_selected = {
        'zone_name': [
            geo_json_selected['features'][0]['properties']['zone'],
        ],
        'default_value': ['start'],
        'log_count': [geomap_data['log_count'][zone]],
        'count': [geomap_data['count'][zone]],
    }

    fig_temp = px.choropleth_mapbox(geomap_data_selected,
                                    geojson=geo_json_selected,
                                    color='default_value',
                                    locations="zone_name",
                                    featureidkey="properties.zone",
                                    mapbox_style="carto-positron",
                                    hover_data=['count'],
                                    zoom=9,
                                    center={"lat": 40.7, "lon": -73.99},
                                    opacity=1.,
                                    )
    fig.add_trace(fig_temp.data[0])
    # Custom tool-tip
    hovertemplate = '<br>Zone: %{location}' \
                    '<br>Number of trips: %{customdata:.3s}' \
                    '<extra></extra>'
    fig.data[1]['hovertemplate'] = hovertemplate

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, coloraxis_showscale=False, showlegend=False)
    return fig


taxi_path = 's3://vaex/taxi/yellow_taxi_2012_zones.hdf5?anon=true'
# override the path, e.g. $ export TAXI_PATH=/data/taxi/yellow_taxi_2012_zones.hdf5
taxi_path = os.environ.get('TAXI_PATH', taxi_path)
df_original = vaex.open(taxi_path)


def create_selection(days, hours):
    df = df_original.copy()
    selection = None
    if hours:
        hour_min, hour_max = hours
        if hour_min > 0:
            df.select((hour_min <= df.pickup_hour), mode='and')
            selection = True
        if hour_max < 23:
            df.select((df.pickup_hour <= hour_max), mode='and')
            selection = True
    if (len(days) > 0) & (len(days) < 7):
        df.select(df.pickup_day.isin(days), mode='and')
        selection = True
    return df, selection


def compute_geomap_data(days, hours):
    df, selection = create_selection(days, hours)
    return df.count(binby=df.pickup_zone, selection=selection)


if __name__ == "__main__":
    zone_initial = 89
    geomap_data_initial = compute_geomap_data([1], [0, 23])
    fig = create_figure_geomap(geomap_data_initial, zone_initial)
    fig.show()


