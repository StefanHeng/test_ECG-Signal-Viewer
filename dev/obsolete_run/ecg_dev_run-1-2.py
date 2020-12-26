import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH

# from memory_profiler import profile

from data_link import *
from ecg_app import EcgApp

D_RNG_INIT = [
    [0, 100000],  # First 50s, given 2000 sample_rate
    [-4000, 4000]  # -4V to 4V
]

ID_GRA = 'graph'
ID_STOR_D_RNG = '_display_range'  # Contains dictionary of each display range
CONF = dict(  # Configuration for figure
    responsive=True,
    scrollZoom=True,
    modeBarButtonsToRemove=['lasso2d', 'select2d', 'autoScale2d', 'toggleSpikelines',
                            'hoverClosestCartesian', 'hoverCompareCartesian'],
    displaylogo=False
)
ID_BTN_FIXY = 'btn_fix_yaxis'
ID_IC_FIXY = 'ic_fix_yaxis'
ID_DIV_OPN = 'div_options'
CNM_IC_LK = 'fas fa-lock'  # Font Awesome
CNM_IC_LKO = 'fas fa-lock-open'
ID_STOR_IS_FIXY = 'id_is_yaxis_fixed'

# Syntactic sugar
T = 'type'  # For pattern matching callbacks
I = 'index'
D = 'data'  # Keywords for Dash and plotly
F = 'figure'
CNM = 'className'

CNM_HD = 'header'
CNM_HDTT = 'header_title'
TXT_HD = 'Ecg Viz'  # Text shown in header
CNM_MNBD = 'body_main'
ID_DIV_PLTS = 'div_plots'
CNM_DIV_LD = 'div_lead'
CNM_LD = 'name-lead'
CNM_DIV_FIG = 'div_figure'
CNM_BTN = 'btn'

ecg_app = EcgApp(__name__)
ecg_app.update_template_dropdown_and_add_options(DATA_PATH.joinpath(record_nm))

app = dash.Dash(
    __name__,
    external_stylesheets=['https://use.fontawesome.com/releases/v5.8.1/css/all.css']
)
app.title = "Dev test run"

# idxs_fig = [6, 4, 5, 3, 9, 16, 35, 20]  # Arbitrary, for testing only, users should spawn all the leads by selection
idxs_fig = range(8)


# Syntactic sugar
def m_id(typ, idx):
    """Generate match id """
    return {T: typ, I: idx}


def mch(id_str):
    """Pattern matching id used in callbacks """
    return {T: id_str, I: MATCH}


app.layout = html.Div([
    # dcc.Store(id=IG_STOR_D_RNG, data={idx: D_RNG_INIT for idx in idxs_fig}),
    html.Div(className=CNM_HD, children=[
        html.Div(TXT_HD, className=CNM_HDTT)
    ]),

    html.Div(className=CNM_MNBD, children=[
        html.Div(id=ID_DIV_PLTS, children=[
            html.Div(className=CNM_DIV_LD, children=[
                # All figure data maintained inside layout variable
                dcc.Store(id=m_id(ID_STOR_D_RNG, idx), data=D_RNG_INIT),
                html.P(ecg_app.curr_rec.lead_nms[idx], className=CNM_LD),
                html.Div(className=CNM_DIV_FIG, children=[
                    html.Div(className=ID_DIV_OPN, children=[
                        html.Div(html.Button(id=m_id(ID_BTN_FIXY, idx), className=CNM_BTN, n_clicks=0, children=[
                            html.I(id=m_id(ID_IC_FIXY, idx), className=CNM_IC_LKO)
                        ])),
                    ]),
                    dcc.Graph(
                        id=m_id(ID_GRA, idx),
                        figure=ecg_app.get_lead_fig(idx, D_RNG_INIT),
                        config=CONF,
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
    Output(mch(ID_STOR_D_RNG), D),
    [Input(mch(ID_GRA), 'relayoutData')],
    [State(mch(ID_STOR_D_RNG), D)],
    prevent_initial_call=True)
def update_limits(relayout_data, d_range):
    if relayout_data is None:
        raise dash.exceptions.PreventUpdate
    elif relayout_data is not None:
        d_range = ecg_app.ui.relayout_data_to_display_range(relayout_data, d_range)
    else:
        if d_range is None:
            d_range = D_RNG_INIT
            raise dash.exceptions.PreventUpdate
    return d_range


@app.callback(
    Output(mch(ID_GRA), F),
    [Input(mch(ID_STOR_D_RNG), D),
     Input(mch(ID_BTN_FIXY), 'n_clicks')],
    [State(mch(ID_GRA), F),
     State(mch(ID_GRA), 'id')])
def update_figure(d_range, n_clicks, fig, id_d):
    changed_id = get_last_changed_ids()
    if ID_STOR_D_RNG in changed_id:  # Only 1 input change is needed each time
        x, y = ecg_app.get_lead_xy_vals(id_d[I], d_range)
        fig[D][0]['x'] = x  # First plot/figure on the graph
        fig[D][0]['y'] = y
    elif ID_BTN_FIXY in changed_id:
        fig['layout']['yaxis']['fixedrange'] = n_clicks % 2 == 1
    return fig


@app.callback(
    Output(mch(ID_IC_FIXY), CNM),
    Input(mch(ID_BTN_FIXY), 'n_clicks'))
def update_fix_yaxis_icon(n_clicks):
    if n_clicks % 2 == 0:  # Init with yaxis unlocked
        return CNM_IC_LKO
    else:
        return CNM_IC_LK


# @profile
def main():
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
