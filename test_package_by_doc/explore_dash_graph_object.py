# -*- coding: utf-8 -*-
# import base64
# import io
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
# import plotly.express as px
# import pandas as pd
# import os
# import numpy as np

# from dash.dependencies import Input, Output  # , State

# from scipy import stats

from ecgrecord import *


def get_ecg_plot(segment, lead):
    print(segment.get_time_axis()[1])
    return go.Figure(
        data=go.Scatter(
            x=segment.get_time_axis()[:100],
            y=lead.get_ecg_values()[:100]
        )
    )


idx_segment = 0
idx_lead = 0
ecg_record = ECGRecord(DATA_PATH.joinpath(selected_record))
key = list(ecg_record.get_segment_keys())[idx_segment]
segment = ecg_record.get_segment(key)
# print(segment.dataset.shape)
time_axis = segment.get_time_axis()
lead = segment.get_lead(idx_lead)

app = dash.Dash(
    __name__
)
server = app.server

app.title = "Explore graph object"

app.layout = html.Div(children=[
    dcc.Graph(
        id='graph-signal',
        figure=get_ecg_plot(segment, lead),
    )
])


if __name__ == "__main__":
    print(len(segment.get_time_axis()))
    server.run(debug=True)
