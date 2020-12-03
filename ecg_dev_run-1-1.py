import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH

# from memory_profiler import profile

from dev_file import *
from ecg_app import EcgApp

PRIMARY = '#FCA912'

D_RNG_INIT = [
    [0, 100000],  # 100s
    [-4000, 4000]  # -4V to 4V
]
# PRESERVE_UI_STATE = 'keep'  # string val assigned arbitrarily
ID_GRA = 'graph'
IG_STOR_D_RNG = '_display_range'
D_CONF = {
    'responsive': True,
    'scrollZoom': True,
    'modeBarButtonsToRemove': ['zoom2d', 'lasso2d', 'select2d', 'autoScale2d', 'toggleSpikelines',
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

idxs_fig = [6, 4, 5, 3, 9, 16, 35, 20]  # Arbitrary, for testing only, users should spawn all the leads by selection

app.layout = html.Div([
    dcc.Store(id=IG_STOR_D_RNG, data=D_RNG_INIT),
    dcc.Store(id=ID_STOR_IS_FIXY, data=False),

    html.Div(className="app-header", children=[
        html.Div('Ecg Viz', className="app-header_title")
    ]),

    html.Div(className='main-body', children=[
        html.Div(id='plots', children=[
            html.Div(className='lead-block', children=[
                html.P(className='name-lead', children=[ecg_app.curr_lead_nms[i]]),
                html.Div(className='figure-container', children=[
                    html.Div(className=ID_DIV_OPN, children=[
                        html.Div(html.Button(id={T: ID_BTN_FIXY, I: i}, className='button', children=[
                            html.I(id={T: ID_IC_FIXY, I: i}, className='fas fa-lock-open', n_clicks=0)
                        ])),
                    ]),
                    dcc.Graph(
                        id={T: ID_GRA, I: i},
                        figure=ecg_app.get_lead_fig(i),
                        config=D_CONF,
                        style=dict(
                            width='95%',
                            height='90%',
                            margin='auto',
                            # border='0.1em solid red'
                        )
                    )
                ])
            ]) for i in idxs_fig
        ])
    ])
])


# @app.callback(
#     Output('dynamic-dropdown-container', 'children'),
#     [Input('dynamic-add-filter', 'n_clicks')],
#     [State('dynamic-dropdown-container', 'children')])
# def display_dropdowns(n_clicks, children):
#     new_element = html.Div([
#         dcc.Dropdown(
#             id={
#                 'type': 'dynamic-dropdown',
#                 'index': n_clicks
#             },
#             options=[{'label': i, 'value': i} for i in ['NYC', 'MTL', 'LA', 'TOKYO']]
#         ),
#         html.Div(
#             id={
#                 'type': 'dynamic-output',
#                 'index': n_clicks
#             }
#         )
#     ])
#     children.append(new_element)
#     return children
#
#
# @app.callback(
#     Output({'type': 'dynamic-output', 'index': MATCH}, 'children'),
#     [Input({'type': 'dynamic-dropdown', 'index': MATCH}, 'value')],
#     [State({'type': 'dynamic-dropdown', 'index': MATCH}, 'id')],
# )
# def display_output(value, id):
#     return html.Div('Dropdown {} = {}'.format(id['index'], value))


# @profile
def main():
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
