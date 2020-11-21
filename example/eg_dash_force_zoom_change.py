import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd

from ecg_plot import DATA_PATH, selected_record
from ecg_app import EcgApp


df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/stockdata.csv')

app = dash.Dash(__name__)
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

id_store_d_range = '_display_range'
DISPLAY_RANGE_INIT = [
    [0, 100000],
    [-4000, 4000]
]
# app.layout = html.Div([
#     dcc.Store(id=id_store_d_range, data=DISPLAY_RANGE_INIT),
#     dcc.Graph(id='graph')
# ])



ecg_app = EcgApp(__name__)
ecg_app.set_curr_record(DATA_PATH.joinpath(selected_record))
idx_lead = 3
plot = ecg_app.add_plot(idx_lead)
fig = ecg_app.get_plot_fig(idx_lead)

id_graph = 'graph'
id_d_range = '_display_range'

app.layout = html.Div(children=[
    html.Div(
        className="app-header",
        children=[
            html.Div('Dev test run', className="app-header_title")
        ]
    ),
    dcc.Store(id=id_store_d_range, data=DISPLAY_RANGE_INIT),

    html.Div(className='main-body', children=[
        html.Div(id='plots', children=[
            html.Div(
                className='figure-block',
                children=[
                    dcc.Graph(
                        id=id_graph,
                        # figure=fig,
                        # config=d_config,
                        # style={
                        #     'width': '95%',
                        #     'height': '90%',
                        #     'margin': 'auto',
                        #     'border': '1px solid red'
                        # }
                    )
                ])
        ])
    ])
])


@app.callback(
    Output(id_d_range, 'data'),
    [Input(id_graph, 'relayoutData')],
    [State(id_d_range, 'data')],
    prevent_initial_call=True)
def update_limits(relayout_data, d_range):
    # print("in update limits")
    if relayout_data is None:
        raise dash.exceptions.PreventUpdate
    elif relayout_data is not None:
        # print("relayout_data is", relayout_data)
        # if 'xaxis.range[0]' in relayout_data:
        #     d_range[0] = [
        #         ecg_app.time_str_to_sample_count(relayout_data['xaxis.range[0]']),
        #         ecg_app.time_str_to_sample_count(relayout_data['xaxis.range[1]'])
        #     ]
        # elif 'yaxis.range[0]' in relayout_data:
        #     d_range[1] = [
        #         ecg_app.time_str_to_sample_count(relayout_data['yaxis.range[0]']),
        #         ecg_app.time_str_to_sample_count(relayout_data['yaxis.range[1]'])
        #     ]
        d_range = ecg_app.to_sample_lim(relayout_data, d_range)
        # print('my_d range', ecg_app.parse_plot_lim(relayout_data, d_range))
        # print(d_range)
        # print("drange is", d_range)
    else:
        if d_range is None:
            d_range = DISPLAY_RANGE_INIT
            raise dash.exceptions.PreventUpdate
    return d_range


@app.callback(
    Output(id_graph, 'figure'),
    Input(id_store_d_range, 'data'))
def update_figure(d_range):
    # print('in update_figure', d_range)
    ecg_app._display_range = d_range
    x, y = ecg_app.get_plot_xy_vals(idx_lead)
    data = [{
        'x': x,
        'y': y,
        'mode': 'lines',
        # 'marker': {'color': color},
        'name': 'AAPL'
    }]
    return {
        'data': data,
        'layout': {
            # `uirevsion` is where the magic happens
            # this key is tracked internally by `dcc.Graph`,
            # when it changes from one update to the next,
            # it resets all of the user-driven interactions
            # (like zooming, panning, clicking on legend items).
            # if it remains the same, then that user-driven UI state
            # doesn't change.
            # it can be equal to anything, the important thing is
            # to make sure that it changes when you want to reset the user
            # state.
            #
            # in this example, we *only* want to reset the user UI state
            # when the user has changed their dataset. That is:
            # - if they toggle on or off reference, don't reset the UI state
            # - if they change the color, then don't reset the UI state
            # so, `uirevsion` needs to change when the `dataset` changes:
            # this is easy to program, we'll just set `uirevision` to be the
            # `dataset` value itself.
            #
            # if we wanted the `uirevision` to change when we add the "reference"
            # line, then we could set this to be `'{}{}'.format(dataset, reference)`
            'uirevision': 'AAPL',

            'legend': {'x': 0, 'y': 1}
        }
    }


if __name__ == '__main__':
    app.run_server(debug=True)
