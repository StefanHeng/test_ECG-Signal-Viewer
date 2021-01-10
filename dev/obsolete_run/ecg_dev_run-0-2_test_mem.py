import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
# import plotly.express as px
import pandas as pd

from memory_profiler import profile

from data_link import *
from ecg_app import EcgApp


@profile
def main():
    DISPLAY_RANGE_INIT = [
        [0, 100000],  # 100s
        [-4000, 4000]  # -4V to 4V
    ]
    # PRESERVE_UI_STATE = 'keep'  # string val assigned arbitrarily
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
    id_graph_fix_y = 'graph_fix_y'
    PRIMARY = '#FCA912'

    ecg_app = EcgApp(__name__)
    ecg_app.update_lead_options_disable_layout_figures(DATA_PATH.joinpath(record_nm))
    idx_lead = 3
    fig = ecg_app.get_lead_fig(idx_lead)

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
                        daq.ToggleSwitch(
                            id=id_graph_fix_y,
                            label='Fix yaxis',
                            color=PRIMARY,
                            value=False
                        ),
                        dcc.Graph(
                            id=id_graph,
                            config=d_config,
                            style=dict(
                                width='95%',
                                height='90%',
                                margin='auto',
                                # border='0.1em solid red'
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
            d_range = ecg_app.ui.relayout_data_to_display_range(relayout_data, d_range)
        else:
            if d_range is None:
                d_range = DISPLAY_RANGE_INIT
                raise dash.exceptions.PreventUpdate
        return d_range


    @app.callback(
        Output(id_store_fig, 'data'),
        [Input(id_store_d_range, 'data'),
         Input(id_graph_fix_y, 'value')])
    def update_figure(d_range, fix_yaxis):
        ecg_app._display_range = d_range
        x, y = ecg_app.get_lead_xy_vals(idx_lead)
        fig['data'][0]['x'] = x
        fig['data'][0]['y'] = y
        fig['layout']['yaxis']['fixedrange'] = fix_yaxis
        return fig


    @app.callback(
        Output(id_graph, 'figure'),
        Input(id_store_fig, 'data'))
    def update_fig(fig_store):
        return fig_store


    app.run_server(debug=True)


if __name__ == "__main__":
    main()
