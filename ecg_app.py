import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH

# import logging

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger('dev')

from dev_file import *
from ecg_record import EcgRecord
from ecg_plot import EcgPlot
from ecg_ui import EcgUi

FA_CSS_LNK = 'https://use.fontawesome.com/releases/v5.8.1/css/all.css'

ID_GRA = 'graph'
ID_STOR_D_RNG = '_display_range'  # Contains dictionary of each display range

CNM_HD = 'header'
CNM_HDTT = 'header_title'
TXT_HD = 'Ecg Viz'  # Text shown in header
CNM_MNBD = 'body_main'

ID_DPD_RECR = 'record-dropdown'
ID_DPD_LD_TEMPL = 'lead-template-dropdown'

ID_DIV_PLTS = 'div_plots'
CNM_DIV_LD = 'div_lead'
CNM_LD = 'name-lead'
CNM_DIV_FIG = 'div_figure'
CNM_GRA = 'plotly-graph'

CONF = dict(  # Configuration for figure
    responsive=True,
    scrollZoom=True,
    modeBarButtonsToRemove=['lasso2d', 'select2d', 'autoScale2d', 'toggleSpikelines',
                            'hoverClosestCartesian', 'hoverCompareCartesian'],
    displaylogo=False
)
D_RNG_INIT = [
    [0, 100000],  # First 50s, given 2000 sample_rate
    [-4000, 4000]  # -4V to 4V
]

CNM_BTN = 'btn'
ID_DIV_FIG_OPN = 'div_fig-options'
ID_BTN_FIXY = 'btn_fix_yaxis'
ID_IC_FIXY = 'ic_fix_yaxis'
CNM_IC_LK = 'fas fa-lock'  # Font Awesome
CNM_IC_LKO = 'fas fa-lock-open'
ID_STOR_IS_FIXY = 'id_is_yaxis_fixed'

# Syntactic sugar
T = 'type'  # For pattern matching callbacks
I = 'index'
D = 'data'  # Keywords for Dash and plotly
F = 'figure'
CNM = 'className'
C = 'children'
V = 'value'


# Syntactic sugar
def m_id(typ, idx):
    """Generate match id """
    return {T: typ, I: idx}


def mch(id_str):
    """Pattern matching id used in callbacks """
    return {T: id_str, I: MATCH}


def join(*class_nms):  # For Dash className
    return ' '.join(class_nms)


class EcgApp:
    """Handles the Dash web app, interface with potentially multiple records

    Encapsulates all UI interactions including HTML layout, callbacks
    """

    LD_TEMPL = {
        # Arbitrary, for testing only, users should spawn all the leads via UI
        'range(8)': range(8),
        'rand': [6, 4, 5, 3, 9, 16, 35, 20]
    }

    def __init__(self, app_name):
        self.curr_recr = None  # Current record
        self.curr_plot = None
        self.idxs_fig = []

        self.app_name = app_name  # No human-readable meaning, name passed into Dash object
        self.app = dash.Dash(self.app_name, external_stylesheets=[FA_CSS_LNK])
        self.app.layout = self._set_layout()
        self._set_callbacks()
        self.ui = EcgUi(self)

    def run(self, debug=False):
        self.app.run_server(debug=debug)

    def _set_layout(self):
        return html.Div([
            html.Div(className=CNM_HD, children=[
                html.Div(TXT_HD, className=CNM_HDTT)
            ]),

            html.Div(className=CNM_MNBD, children=[
                dcc.Dropdown(
                    id=ID_DPD_RECR, value=record_nm,
                    options=[{'label': f'{KW_DEV}{record_nm}', V: record_nm}]
                ),
                dcc.Dropdown(
                    id=ID_DPD_LD_TEMPL, disabled=True,
                    options=[
                        {'label': KW_DEV + 'range(8)', V: 'range(8)'},
                        {'label': KW_DEV + 'random', V: 'rand'}
                    ]
                ),
                html.Div(id=ID_DIV_PLTS, children=[
                    self.get_fig_layout(idx) for idx in self.idxs_fig
                ])
            ])
        ])

    def get_fig_layout(self, idx):
        return html.Div(
            className=CNM_DIV_LD, children=[
                # All figure data maintained inside layout variable
                dcc.Store(id=m_id(ID_STOR_D_RNG, idx), data=D_RNG_INIT),
                html.P(self.curr_recr.lead_nms[idx], className=CNM_LD),
                html.Div(className=CNM_DIV_FIG, children=[
                    html.Div(className=ID_DIV_FIG_OPN, children=[
                        html.Div(
                            html.Button(id=m_id(ID_BTN_FIXY, idx), className=CNM_BTN, n_clicks=0, children=[
                                html.I(id=m_id(ID_IC_FIXY, idx), className=CNM_IC_LKO)
                            ])),
                    ]),
                    dcc.Graph(
                        id=m_id(ID_GRA, idx), className=CNM_GRA, config=CONF,
                        figure=self.get_lead_fig(idx, D_RNG_INIT)
                    )
                ])
            ])

    def _set_callbacks(self):
        self.app.callback(
            Output(mch(ID_STOR_D_RNG), D),
            [Input(mch(ID_GRA), 'relayoutData')],
            [State(mch(ID_STOR_D_RNG), D)],
            prevent_initial_call=True
        )(self.update_lims)
        self.app.callback(
            Output(ID_DPD_LD_TEMPL, 'disabled'),
            Input(ID_DPD_RECR, V)
        )(self.set_record)
        self.app.callback(
            Output(ID_DIV_PLTS, C),
            Input(ID_DPD_LD_TEMPL, V),
            prevent_initial_call=True
        )(self._load_figs)
        self.app.callback(
            Output(mch(ID_IC_FIXY), CNM),
            Input(mch(ID_BTN_FIXY), 'n_clicks')
        )(self.update_fix_yaxis_icon)
        self.app.callback(
            Output(mch(ID_GRA), F),
            [Input(mch(ID_STOR_D_RNG), D),
             Input(mch(ID_BTN_FIXY), 'n_clicks')],
            [State(mch(ID_GRA), F),
             State(mch(ID_GRA), 'id')]
        )(self.update_figure)

    def set_record(self, recr_nm):
        """Current record selected to display. Previous record data overridden """
        if recr_nm is None:
            return True
        else:
            self.curr_recr = EcgRecord(DATA_PATH.joinpath(recr_nm))
            self.curr_plot = EcgPlot(self.curr_recr, self)  # A `plot` servers a record
            return False

    def _load_figs(self, key_templ):
        """Set up multiple figures in the APP, original figures shown overridden """
        self.idxs_fig = self.LD_TEMPL[key_templ]
        return [self.get_fig_layout(idx) for idx in self.idxs_fig]

    def get_lead_fig(self, idx_lead, display_range):
        """
        :param idx_lead: index of lead as stored in .h5 datasets
        :param display_range: range of sample_counts, inclusive start and end

        .. note:: A valid range has values in [0, sum of all samples across the entire ecg_record),
        one-to-one correspondence with time by `sample_rate`

        :return: dictionary that represents a plotly graph
        """
        strt, end = display_range[0]
        return self.curr_plot.get_fig(idx_lead, strt, end)

    def get_lead_xy_vals(self, idx_lead, display_range):
        strt, end = display_range[0]
        # determine if optimization is needed for large sample_range
        return self.curr_plot.get_xy_vals(idx_lead, strt, end)

    @staticmethod
    def get_changed_ids():
        return [p['prop_id'] for p in dash.callback_context.triggered][0]

    def update_lims(self, relayout_data, d_range):
        return self.ui.to_sample_lim(relayout_data, d_range)
        # if relayout_data is None:
        #     raise dash.exceptions.PreventUpdate
        # elif relayout_data is not None:
        #     d_range = self.ui.to_sample_lim(relayout_data, d_range)
        # else:
        #     if d_range is None:
        #         d_range = D_RNG_INIT
        #         raise dash.exceptions.PreventUpdate
        # return d_range

    def update_figure(self, d_range, n_clicks, fig, id_d):
        changed_id = self.get_changed_ids()
        if ID_STOR_D_RNG in changed_id:  # Only 1 input change is needed each time
            x, y = self.get_lead_xy_vals(id_d[I], d_range)
            fig[D][0]['x'] = x  # First plot/figure on the graph
            fig[D][0]['y'] = y
        elif ID_BTN_FIXY in changed_id:
            fig['layout']['yaxis']['fixedrange'] = n_clicks % 2 == 1
        return fig

    @staticmethod
    def update_fix_yaxis_icon(n_clicks):
        if n_clicks % 2 == 0:  # Init with yaxis unlocked
            return CNM_IC_LKO
        else:
            return CNM_IC_LK
