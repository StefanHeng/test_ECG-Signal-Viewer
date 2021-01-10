import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
# import plotly.express as px
import pandas as pd

from data_link import *
from ecg_app import EcgApp

DISPLAY_RANGE_INIT = [
    [0, 100000],  # 100s
    [-4000, 4000]  # -4V to 4V
]
id_graph = 'graph'
id_store_plot_vals = 'vals'
id_store_graph_lim = 'ori_relayoutData'  # To force zoom on the same place after update
id_store_d_range = '_display_range'
d_config = {
    'responsive': True,
    'scrollZoom': True,
    'modeBarButtonsToRemove': ['zoom2d', 'lasso2d', 'select2d', 'autoScale2d', 'toggleSpikelines',
                               'hoverClosestCartesian', 'hoverCompareCartesian'],
    'displaylogo': False
}

ecg_app = EcgApp(__name__)
ecg_app.update_lead_options_disable_layout_figures(DATA_PATH.joinpath(record_nm))
idx_lead = 3
plot = ecg_app.add_plot(idx_lead)
fig = ecg_app.get_lead_fig(idx_lead)
x_vals, y_vals = ecg_app.get_lead_xy_vals(idx_lead)
d_vals = {'x_vals': x_vals, 'y_vals': y_vals}

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
    dcc.Store(id=id_store_graph_lim),
    dcc.Store(id=id_store_plot_vals, data=d_vals),

    html.Div(className='main-body', children=[
        html.Div(id='plots', children=[
            html.Div(
                className='figure-block',
                children=[
                    dcc.Graph(
                        id=id_graph,
                        figure=fig,
                        config=d_config,
                        style={
                            'width': '95%',
                            'height': '90%',
                            'margin': 'auto',
                            'border': '1px solid red'
                        }
                    )
                ])
        ])
    ])
])


@app.callback(
    [Output(id_store_d_range, 'data'),
     Output(id_store_graph_lim, 'data')],
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
    return d_range, relayout_data


@app.callback(
    [Output(id_graph, 'figure'),
     Output(id_store_plot_vals, 'data')],
    [Input(id_store_d_range, 'data')],
    [State(id_store_plot_vals, 'data'),
     State(id_store_graph_lim, 'data')],
    prevent_initial_call=True)
def update_figure(d_range, dict_vals, graph_lim_ori):
    ecg_app._display_range = d_range
    x, y = ecg_app.get_lead_xy_vals(idx_lead)
    dict_vals['x_vals'] = x
    dict_vals['y_vals'] = y
    fig.update_traces(
        overwrite=True,
        x=dict_vals['x_vals'],
        y=dict_vals['y_vals']
    )
    # fig.update_layout(layout=graph_lim_ori)
    # fig['layout'] = graph_lim_ori
    return fig, dict_vals


if __name__ == "__main__":
    app.run_server(debug=True)
