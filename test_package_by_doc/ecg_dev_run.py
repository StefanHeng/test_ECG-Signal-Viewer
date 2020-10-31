import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
# import plotly.express as px
# import pandas as pd

import ecg_plot

if __name__ == "__main__":
    fig = ecg_plot.EcgPlot.example()

    app = dash.Dash(
        __name__
    )
    server = app.server

    app.title = "development test run"

    app.layout = html.Div(children=[
        dcc.Graph(
            id='graph-signal',
            figure=fig,
        )
    ])

    server.run(debug=True)
