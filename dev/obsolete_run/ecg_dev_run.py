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
ecg_app.set_record(DATA_PATH.joinpath(record_nm))
idx_lead = 3
plot = ecg_app.add_plot(idx_lead)
fig = ecg_app.get_lead_fig(idx_lead)

app = dash.Dash(
    __name__
)
server = app.server

app.title = "development test run"

app.layout = html.Div(children=[
    dcc.Store(id=id_d_range, data=DISPLAY_RANGE_INIT),
    dcc.Graph(
        id=id_fig,
        figure=fig,
        config=d_config
    )
])


@app.callback(
    Output(id_d_range, 'data'),
    [Input(id_fig, 'relayoutData')],
    [State(id_d_range, 'data')],
    prevent_initial_call=True)
def update_limits(relayout_data, d_range):
    # print("in update limits")
    if relayout_data is None:
        raise dash.exceptions.PreventUpdate
    elif relayout_data is not None:
        # print("relayout_data is", relayout_data)
        if 'xaxis.range[0]' in relayout_data:
            d_range[0] = [
                ecg_app._time_str_to_sample_count(relayout_data['xaxis.range[0]']),
                ecg_app._time_str_to_sample_count(relayout_data['xaxis.range[1]'])
            ]
        elif 'yaxis.range[0]' in relayout_data:
            d_range[1] = [
                ecg_app._time_str_to_sample_count(relayout_data['yaxis.range[0]']),
                ecg_app._time_str_to_sample_count(relayout_data['yaxis.range[1]'])
            ]
        # print("drange is", d_range)
    else:
        if d_range is None:
            d_range = DISPLAY_RANGE_INIT
            raise dash.exceptions.PreventUpdate
    return d_range


@app.callback(
    Output(id_fig, 'figure'),
    [Input(id_d_range, 'data')],
    prevent_initial_call=True)
def update_figure(d_range):
    # print("in create fig")
    t = pd.Timestamp(d_range[0][0])
    # print(t.microsecond / 500)  # sample count
    ecg_app._display_range = d_range
    # print(ecg_app._display_range)
    return ecg_app.get_lead_fig(idx_lead)


if __name__ == "__main__":
    app.run_server(debug=True)
