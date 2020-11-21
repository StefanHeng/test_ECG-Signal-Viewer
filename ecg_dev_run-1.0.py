import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH

import plotly.graph_objs as go
# import plotly.express as px
# import pandas as pd

from dev_file import *
from ecg_app import EcgApp

DISPLAY_RANGE_INIT = [
    [0, 100000],  # 100s
    [-4000, 4000]  # -4V to 4V
]
id_fig = 'figure'
id_d_range = '_display_range'
d_config = {
    'responsive': True,
    'scrollZoom': True,
    'modeBarButtonsToRemove': ['zoom2d', 'lasso2d', 'select2d', 'autoScale2d', 'toggleSpikelines',
                               'hoverClosestCartesian', 'hoverCompareCartesian'],
    'displaylogo': False
}

ecg_app = EcgApp(__name__)
ecg_app.set_curr_record(DATA_PATH.joinpath(selected_record))
idxs_fig = [6, 4, 5, 3, 9, 16, 35, 20]  # Arbitrary, for testing only, users should spawn all the leads by selection


app = dash.Dash(__name__, suppress_callback_exceptions=True)

figs = [

]

app.layout = html.Div([
    html.Div(
        className="app-header",
        children=[
            html.Div('ECG Signal Viewer', className="app-header_title")
        ]
    ),
    html.Div(className='main-body', children=[
        html.Div(id='plots', children=[
            html.Div(
                className='figure-block',
                children=[
                    dcc.Graph(
                        id=str(i),
                        figure=ecg_app.get_lead_fig(i),
                        config=d_config,
                        style=dict(
                            width='95%',
                            height='90%',
                            margin='auto',
                            border='0.1em solid red'
                        )
                    )
                ]) for i in idxs_fig
            # html.Div(children="test") for i in idxs_fig
        ])
    ])
])

# @app.callback(
#     Output('dynamic-dropdown-container', 'children'),
#     [Input('dynamic-add-filter', 'n_clicks')],
#     [State('dynamic-dropdown-container', 'children')])
# def display_dropdowns(n_clicks, children):
#     new_element = html.Div([
#         dcc.Dropdown(
#             id={
#                 'type': 'dynamic-dropdown',
#                 'index': n_clicks
#             },
#             options=[{'label': i, 'value': i} for i in ['NYC', 'MTL', 'LA', 'TOKYO']]
#         ),
#         html.Div(
#             id={
#                 'type': 'dynamic-output',
#                 'index': n_clicks
#             }
#         )
#     ])
#     children.append(new_element)
#     return children
#
#
# @app.callback(
#     Output({'type': 'dynamic-output', 'index': MATCH}, 'children'),
#     [Input({'type': 'dynamic-dropdown', 'index': MATCH}, 'value')],
#     [State({'type': 'dynamic-dropdown', 'index': MATCH}, 'id')],
# )
# def display_output(value, id):
#     return html.Div('Dropdown {} = {}'.format(id['index'], value))


if __name__ == "__main__":
    app.title = "development test run"
    app.run_server(debug=True)
