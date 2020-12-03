import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH

# from memory_profiler import profile

from dev_file import *
from ecg_app import EcgApp

D_RNG_INIT = [
    [0, 100000],  # 100s
    [-4000, 4000]  # -4V to 4V
]
# PRESERVE_UI_STATE = 'keep'  # string val assigned arbitrarily
ID_GRA = 'graph'
IG_STOR_D_RNG = '_display_range'  # Contains dictionary of each display range
D_CONF = {
    'responsive': True,
    'scrollZoom': True,
    'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'autoScale2d', 'toggleSpikelines',
                               'hoverClosestCartesian', 'hoverCompareCartesian'],
    'displaylogo': False
}
ID_BTN_FIXY = 'btn_fix_yaxis'
ID_IC_FIXY = 'ic_fix_yaxis'
ID_DIV_OPN = 'div_options'
CLSNM_IC_LK = 'fas fa-lock'
CLSNM_IC_LKO = 'fas fa-lock-open'
ID_STOR_IS_FIXY = 'id_is_yaxis_fixed'

T = 'type'
I = 'index'

ecg_app = EcgApp(__name__)
ecg_app.set_curr_record(DATA_PATH.joinpath(selected_record))

app = dash.Dash(
    __name__,
    external_stylesheets=['https://use.fontawesome.com/releases/v5.8.1/css/all.css']
)
app.title = "Dev test run"

# idxs_fig = [6, 4, 5, 3, 9, 16, 35, 20]  # Arbitrary, for testing only, users should spawn all the leads by selection
idxs_fig = range(8)

app.layout = html.Div([
    # dcc.Store(id=IG_STOR_D_RNG, data={idx: D_RNG_INIT for idx in idxs_fig}),
    html.Div(className="app-header", children=[
        html.Div('Ecg Viz', className="app-header_title")
    ]),

    html.Div(className='main-body', children=[
        html.Div(id='plots', children=[
            html.Div(className='lead-block', children=[
                dcc.Store(id={T: IG_STOR_D_RNG, I: idx}, data=D_RNG_INIT),
                html.P(ecg_app.curr_lead_nms[idx], className='name-lead'),
                html.Div(className='figure-container', children=[
                    html.Div(className=ID_DIV_OPN, children=[
                        html.Div(html.Button(id={T: ID_BTN_FIXY, I: idx}, className='button', n_clicks=0, children=[
                            html.I(id={T: ID_IC_FIXY, I: idx}, className='fas fa-lock-open')
                        ])),
                    ]),
                    dcc.Graph(
                        id={T: ID_GRA, I: idx},
                        figure=ecg_app.get_lead_fig(idx, D_RNG_INIT),
                        config=D_CONF,
                        style=dict(
                            width='95%',
                            height='90%',
                            margin='auto',
                            # border='0.1em solid red'
                        )
                    )
                ])
            ]) for idx in idxs_fig
        ])
    ])
])


def get_last_changed_ids():
    return [p['prop_id'] for p in dash.callback_context.triggered][0]


@app.callback(
    Output({T: IG_STOR_D_RNG, I: MATCH}, 'data'),
    [Input({T: ID_GRA, I: MATCH}, 'relayoutData')],
    [State({T: IG_STOR_D_RNG, I: MATCH}, 'data')],
    prevent_initial_call=True)
def update_limits(relayout_data, d_range):
    if relayout_data is None:
        raise dash.exceptions.PreventUpdate
    elif relayout_data is not None:
        d_range = ecg_app.ui.to_sample_lim(relayout_data, d_range)
    else:
        if d_range is None:
            d_range = D_RNG_INIT
            raise dash.exceptions.PreventUpdate
    return d_range


@app.callback(
    Output({T: ID_GRA, I: MATCH}, 'figure'),
    [Input({T: IG_STOR_D_RNG, I: MATCH}, 'data'),
     Input({T: ID_BTN_FIXY, I: MATCH}, 'n_clicks')],
    [State({T: ID_GRA, I: MATCH}, 'figure'),
     State({T: ID_GRA, I: MATCH}, 'id')])
def update_figure(d_range, n_clicks, f, id_d):
    changed_id = get_last_changed_ids()
    if IG_STOR_D_RNG in changed_id:  # Only 1 input change is needed each time
        x, y = ecg_app.get_lead_xy_vals(id_d[I], d_range)
        f['data'][0]['x'] = x
        f['data'][0]['y'] = y
    elif ID_BTN_FIXY in changed_id:
        f['layout']['yaxis']['fixedrange'] = n_clicks % 2 == 1
    return f


@app.callback(
    Output({T: ID_IC_FIXY, I: MATCH}, 'className'),
    Input({T: ID_BTN_FIXY, I: MATCH}, 'n_clicks'))
def update_fix_yaxis_icon(n_clicks):
    if n_clicks % 2 == 0:  # Init with yaxis unlocked
        return CLSNM_IC_LKO
    else:
        return CLSNM_IC_LK


# @profile
def main():
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
