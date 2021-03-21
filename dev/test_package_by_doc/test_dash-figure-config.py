import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import numpy as np


if __name__ == "__main__":
    y = np.random.uniform(-1, 1, 600)
    x = np.arange(len(y))

    trace = go.Scatter(x=x, y=y,
                       mode='lines+markers',
                       # mode='lines'
    )
    data = [trace, go.Scatter(
            x=[1, 2, 3],
            y=[1, 3, 1],
            # mode='markers+lines',
            # mode='lines'
    )
    ]
    # fig = go.Figure(data=data)
    fig = go.Figure()
    fig.add_trace(trace)
    fig.show()
