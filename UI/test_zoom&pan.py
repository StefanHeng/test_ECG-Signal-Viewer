import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import numpy as np

import os
from flask_caching import Cache


app = dash.Dash(__name__+'test zoom&pan')

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})
CACHE_TIMEOUT = int(os.environ.get('DASH_CACHE_TIMEOUT', '60'))

DISPLAY_RANGE_INIT = [
    [0, 40],
    [-20, 20]
]
id_fig = 'figure'
id_d_range = '_display_range'
d_config = {
    'scrollZoom': True,
    'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
    'displaylogo': False
}


def create_figure(d_range):
    # print(d_range)
    strt, end = d_range[0]
    x = np.linspace(strt, end, num=int(end-strt + 1)*10);
    y = 10 * np.sin(x / 10)

    fig = go.Figure(
        data=go.Scatter(
            x=x,
            y=y
        )
    )
    fig.update_layout(dragmode='pan')
    return fig


fig_init = create_figure(DISPLAY_RANGE_INIT)
fig_init.update_layout(dragmode='pan')

app.layout = html.Div(className='app-body', children=[
    dcc.Store(id=id_d_range, data=DISPLAY_RANGE_INIT),
    html.Div(className="row", children=[
        html.Div(className="seven columns pretty_container", children=[
            dcc.Graph(
                id=id_fig,
                figure=fig_init,
                config=d_config)
        ])
    ]),
])


@app.callback(
    Output(id_d_range, 'data'),
    [Input(id_fig, 'relayoutData')],
    [State(id_d_range, 'data')],
    prevent_initial_call=True)
def update_limits(relayout_data, d_range):
    # print('in update_limits:', d_range)
    # print(relayout_data)
    if relayout_data is None:
        raise dash.exceptions.PreventUpdate
    elif relayout_data is not None:
        if 'xaxis.range[0]' in relayout_data:
            d_range[0] = [relayout_data['xaxis.range[0]'], relayout_data['xaxis.range[1]']]
        elif 'yaxis.range[0]' in relayout_data:
            d_range[1] = [relayout_data['yaxis.range[0]'], relayout_data['yaxis.range[1]']]
    else:
        if d_range is None:
            d_range = DISPLAY_RANGE_INIT
            raise dash.exceptions.PreventUpdate
    return d_range


@app.callback(
    Output(id_fig, 'figure'),
    Input(id_d_range, 'data'),
    prevent_initial_call=True)
def update_heatmap_figure(d_range):
    # print('in update_figure:', d_range)
    return create_figure(d_range)


if __name__ == '__main__':
    app.run_server(debug=True)

