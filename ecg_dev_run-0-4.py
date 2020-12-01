import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd

from memory_profiler import profile

from dev_file import *
from ecg_app import EcgApp

PRIMARY = '#FCA912'

DISP_RANGE_INIT = [
    [0, 100000],  # 100s
    [-4000, 4000]  # -4V to 4V
]
# PRESERVE_UI_STATE = 'keep'  # string val assigned arbitrarily
ID_GRA = 'graph'
IG_STOR_D_RANGE = '_display_range'
D_CONFIG = {
    'responsive': True,
    'scrollZoom': True,
    'modeBarButtonsToRemove': ['zoom2d', 'lasso2d', 'select2d', 'autoScale2d', 'toggleSpikelines',
                               'hoverClosestCartesian', 'hoverCompareCartesian'],
    'displaylogo': False
}
ID_BTN_FIX_YAXIS = 'btn_fix_yaxis'
ID_IC_FIX_YAXIS = 'ic_fix_yaxis'
ID_DIV_OPTIONS = 'div_options'
CLSNM_IC_LOCK = 'fas fa-lock'
CLSNM_IC_LOCK_O = 'fas fa-lock-open'
ID_STOR_IS_YAXIS_FIXED = 'id_is_yaxis_fixed'

ecg_app = EcgApp(__name__)
ecg_app.set_curr_record(DATA_PATH.joinpath(selected_record))
idx_lead = 3
fig = ecg_app.get_lead_fig(idx_lead)

app = dash.Dash(
    __name__,
    external_stylesheets=['https://use.fontawesome.com/releases/v5.8.1/css/all.css']
)

server = app.server

app.title = "Dev test run"

app.layout = html.Div(children=[
    dcc.Store(id=IG_STOR_D_RANGE, data=DISP_RANGE_INIT),
    dcc.Store(id=ID_STOR_IS_YAXIS_FIXED, data=False),

    html.Div(className="app-header", children=[
        html.Div('Ecg Viz', className="app-header_title")
    ]),

    html.Div(className='main-body', children=[
        html.Div(id='plots', children=[
            html.Div(className='figure-block', children=[
                html.P(className='name-lead', children=[ecg_app.curr_lead_nms[idx_lead]]),
                html.Div(className='figure-container', children=[
                    html.Div(className=ID_DIV_OPTIONS, children=[
                        html.Div(html.Button(id=ID_BTN_FIX_YAXIS, n_clicks=0, className='button', children=[
                            html.I(id=ID_IC_FIX_YAXIS, className='fas fa-lock-open')
                        ])),
                    ]),
                    dcc.Graph(
                        id=ID_GRA,
                        figure=fig,
                        config=D_CONFIG,
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
])


@app.callback(
    Output(IG_STOR_D_RANGE, 'data'),
    [Input(ID_GRA, 'relayoutData')],
    [State(IG_STOR_D_RANGE, 'data')],
    prevent_initial_call=True)
def update_limits(relayout_data, d_range):
    if relayout_data is None:
        raise dash.exceptions.PreventUpdate
    elif relayout_data is not None:
        d_range = ecg_app.ui.to_sample_lim(relayout_data, d_range)
    else:
        if d_range is None:
            d_range = DISP_RANGE_INIT
            raise dash.exceptions.PreventUpdate
    return d_range


@app.callback(
    Output(ID_GRA, 'figure'),
    [Input(IG_STOR_D_RANGE, 'data'),
     Input(ID_IC_FIX_YAXIS, 'n_clicks')],
    State(ID_GRA, 'figure'))
def update_figure(d_range, n_clicks, f):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if IG_STOR_D_RANGE in changed_id:  # Only 1 input change is needed each time
        ecg_app._display_range = d_range
        x, y = ecg_app.get_lead_xy_vals(idx_lead)
        f['data'][0]['x'] = x
        f['data'][0]['y'] = y
    elif ID_IC_FIX_YAXIS in changed_id:
        f['layout']['yaxis']['fixedrange'] = n_clicks % 2 == 1
    return f


@app.callback(
    Output(ID_IC_FIX_YAXIS, 'className'),
    Input(ID_BTN_FIX_YAXIS, 'n_clicks'))
def update_fix_yaxis_icon(n_clicks):
    if n_clicks % 2 == 0:  # Init with yaxis unlocked
        return CLSNM_IC_LOCK_O
    else:
        return CLSNM_IC_LOCK


# @profile
def main():
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
