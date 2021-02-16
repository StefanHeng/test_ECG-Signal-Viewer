import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH

# from memory_profiler import profile

from ecg_app import *

ID_BBX_DIV_OPN = 'div_options-bound-box'
ID_DIV_OPN = 'div_options'
CNM_IC_BR = 'fas fa-bars'
ID_BTN_OPN = 'btn_options'
ID_IC_OPN = 'ic_options'

ANM_OPQY = 'opaque_1'  # Transition achieved by changing class
ANM_OPQN = 'opaque_0'
ANM_DIV_OPN_EXPW = 'div_options_expand-width'
ANM_DIV_OPN_CLPW = 'div_options_collapse-width'
ANM_BTN_OPN_ROTS = 'btn_options_rotate_start'
ANM_BTN_OPN_ROTE = 'btn_options_rotate_end'

CNM_MY_DPD = 'my_dropdown'


# @profile
def main():
    ecg_app = EcgApp(__name__)
    ecg_app.app.title = "Dev test run"
    ecg_app.app.layout = html.Div([
        html.Div(className=CNM_HD, children=[
            html.Div(TXT_HD, className=ID_HDTT)
        ]),

        html.Div(id=ID_BBX_DIV_OPN, children=[
            html.Button(id=ID_BTN_OPN, className=CNM_BTN, n_clicks=0, children=[
                html.I(id=ID_IC_OPN, className=CNM_IC_BR)
            ]),
            html.Div(id=ID_DIV_OPN, children=[
                dcc.Dropdown(
                    id=ID_DPD_RECR, className=CNM_MY_DPD, value=record_nm, placeholder='Select patient record file',
                    options=[{'label': f'{KW_DEV}{record_nm}', V: record_nm}]
                ),
                dcc.Dropdown(
                    id=ID_DPD_LD_TEMPL, className=CNM_MY_DPD, disabled=True, placeholder='Select lead/channel',
                    options=[
                        {'label': KW_DEV + 'range(8)', V: 'range(8)'},
                        {'label': KW_DEV + 'random', V: 'rand'}
                    ]
                )
            ]),
        ]),

        html.Div(className=CNM_MNBD, children=[
            html.Div(id=ID_DIV_PLTS, children=[
                ecg_app.get_fig_layout(idx) for idx in ecg_app.idxs_lead
            ])
        ])
    ])

    @ecg_app.app.callback(
        [Output(ID_IC_OPN, CNM),
         Output(ID_DIV_OPN, CNM)],
        Input(ID_BTN_OPN, 'n_clicks'))
    def update_div_options(n_clicks):
        if n_clicks % 2 == 0:
            return join(CNM_IC_BR, ANM_IC_OPN_ROTE), join(ANM_DIV_OPN_EXPW, ANM_OPQY)
        else:
            return join(CNM_IC_BR, ANM_IC_OPN_ROTS), join(ANM_DIV_OPN_CLPW, ANM_OPQN)

    ecg_app.run(True)





if __name__ == "__main__":
    main()
