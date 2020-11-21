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

import ecg_record


def get_ecg_plot(segment, lead):
    return go.Figure(
        data=go.Scatter(
            x=segment.to_time_axis(),
            y=lead.get_ecg_values()
        )
    )


if __name__ == "__main__":
    ecg_record, seg, lead = ecg_record.EcgRecord.example()

    app = dash.Dash(
        __name__
    )
    server = app.server

    app.title = "Explore graph object"

    app.layout = html.Div(children=[
        dcc.Graph(
            id='graph-signal',
            figure=get_ecg_plot(seg, lead),
        )
    ])

    server.run(debug=True)
