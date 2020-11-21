import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
# import plotly.express as px
import pandas as pd

from dev_file import *
from ecg_app import EcgApp

DISPLAY_RANGE_INIT = [
    [0, 100000],  # 100s
    [-4000, 4000]  # -4V to 4V
]
PRESERVE_UI_STATE = 'keep'  # string val assigned arbitrarily
id_graph = 'graph'
id_store_d_range = '_display_range'
id_store_fig = 'id_store_fig'
d_config = {
    'responsive': True,
    'scrollZoom': True,
    'modeBarButtonsToRemove': ['zoom2d', 'lasso2d', 'select2d', 'autoScale2d', 'toggleSpikelines',
                               'hoverClosestCartesian', 'hoverCompareCartesian'],
    'displaylogo': False
}

ecg_app = EcgApp(__name__)
ecg_app.set_curr_record(DATA_PATH.joinpath(selected_record))
idx_lead = 3
plot = ecg_app.add_plot(idx_lead)
fig = ecg_app.get_plot_fig(idx_lead)
x_vals, y_vals = ecg_app.get_plot_xy_vals(idx_lead)

app = dash.Dash(
    __name__
)
server = app.server

app.title = "development test run"

app.layout = html.Div(children=[
    html.Div(
        className="app-header",
        children=[
            html.Div('Dev test run', className="app-header_title")
        ]
    ),
    dcc.Store(id=id_store_d_range, data=DISPLAY_RANGE_INIT),
    dcc.Store(id=id_store_fig, data=fig),

    html.Div(className='main-body', children=[
        html.Div(id='plots', children=[
            html.Div(
                className='figure-block',
                children=[
                    dcc.Graph(
                        id=id_graph,
                        config=d_config,
                        style=dict(
                            width='95%',
                            height='90%',
                            margin='auto',
                            border='0.1em solid red'
                        )
                    )
                ])
        ])
    ])
])


@app.callback(
    Output(id_store_d_range, 'data'),
    [Input(id_graph, 'relayoutData')],
    [State(id_store_d_range, 'data')],
    prevent_initial_call=True)
def update_limits(relayout_data, d_range):
    if relayout_data is None:
        raise dash.exceptions.PreventUpdate
    elif relayout_data is not None:
        d_range = ecg_app.to_sample_lim(relayout_data, d_range)
    else:
        if d_range is None:
            d_range = DISPLAY_RANGE_INIT
            raise dash.exceptions.PreventUpdate
    return d_range


@app.callback(
    Output(id_store_fig, 'data'),
    Input(id_store_d_range, 'data'))
def update_figure(d_range):
    ecg_app._display_range = d_range
    x, y = ecg_app.get_plot_xy_vals(idx_lead)
    fig['data'][0]['x'] = x
    fig['data'][0]['y'] = y
    return fig


@app.callback(
    Output(id_graph, 'figure'),
    Input(id_store_fig, 'data'))
def update_fig(fig_store):
    return fig_store


if __name__ == "__main__":
    app.run_server(debug=True)
