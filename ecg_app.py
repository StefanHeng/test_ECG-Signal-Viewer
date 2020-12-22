import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH

# import logging

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger('dev')

from data_link import *
from dev_helper import *
from ecg_record import EcgRecord
from ecg_plot import EcgPlot
from ecg_ui import EcgUi

FA_CSS_LNK = 'https://use.fontawesome.com/releases/v5.8.1/css/all.css'

CNM_HD = 'header'
CNM_HDTT = 'header_title'
TXT_HD = 'Ecg Viz'  # Text shown in header
CNM_MNBD = 'body_main'

ID_BBX_DIV_OPN = 'div_options-bound-box'
ID_DIV_OPN = 'div_options'
CNM_IC_BR = 'fas fa-bars'
ID_BTN_OPN = 'btn_options'
ID_IC_OPN = 'ic_options'

ID_DPD_RECR = 'record-dropdown'
ID_DPD_LD_TEMPL = 'lead-template-dropdown'

ID_DIV_PLTS = 'div_plots'
CNM_DIV_LD = 'div_lead'
CNM_DIV_LDNM = 'div_lead-name'
CNM_LD = 'lead-name'
CNM_DIV_TMB = 'div_graph-thumbnail'
CNM_DIV_FIG = 'div_graph'
CNM_TMB = 'channel-graph-thumbnail'
CNM_GRA = 'channel-graph'
ID_TMB = 'figure-thumbnail'
ID_GRA = 'graph'
ID_STOR_D_RNG = '_display_range'  # Contains dictionary of each display range

ANM_OPQY = 'opaque_1'  # Transition achieved by changing class
ANM_OPQN = 'opaque_0'
ANM_DIV_OPN_EXPW = 'div_options_expand-width'
ANM_DIV_OPN_CLPW = 'div_options_collapse-width'
ANM_BTN_OPN_ROTS = 'btn_options_rotate_start'
ANM_BTN_OPN_ROTE = 'btn_options_rotate_end'

CONF = dict(  # Configuration for figure
    responsive=True,
    scrollZoom=True,
    modeBarButtonsToRemove=['lasso2d', 'select2d', 'autoScale2d', 'toggleSpikelines',
                            'hoverClosestCartesian', 'hoverCompareCartesian'],
    displaylogo=False
)

CNM_BTN = 'btn'
CNM_MY_DPD = 'my_dropdown'
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
NC = 'n_clicks'
L = 'label'


# Syntactic sugar
def m_id(typ, idx):
    """Generate match id """
    return {T: typ, I: idx}


def mch(id_str):
    """Pattern matching id used in callbacks """
    return {T: id_str, I: MATCH}


def join(*class_nms):  # For Dash className
    """Join string arguments into whitespace-separated single string """
    return ' '.join(class_nms)


DEV_TML_S = 'single'
DEV_TML_RG = 'range(8)'
DEV_TML_RD = 'rand'


class EcgApp:
    """Handles the Dash web app, interface with potentially multiple records

    Encapsulates all UI interactions including HTML layout, callbacks
    """

    LD_TEMPL = {
        # Arbitrary, for testing only, users should spawn all the leads via UI
        DEV_TML_S: [3],
        DEV_TML_RG: range(8),
        DEV_TML_RD: [6, 4, 5, 3, 9, 16, 35, 20]
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

            html.Div(id=ID_BBX_DIV_OPN, children=[
                html.Button(id=ID_BTN_OPN, className=CNM_BTN, n_clicks=0, children=[
                    html.I(id=ID_IC_OPN, className=CNM_IC_BR)
                ]),
                html.Div(id=ID_DIV_OPN, children=[
                    dcc.Dropdown(
                        id=ID_DPD_RECR, className=CNM_MY_DPD, value=record_nm, placeholder='Select patient record file',
                        options=[{L: f'{dev(record_nm)}', V: record_nm}]
                    ),
                    dcc.Dropdown(
                        id=ID_DPD_LD_TEMPL, className=CNM_MY_DPD, disabled=True, placeholder='Select lead/channel',
                        options=[
                            {L: f'{dev(DEV_TML_S)}', V: DEV_TML_S},
                            {L: f'{dev(DEV_TML_RG)}', V: DEV_TML_RG},
                            {L: f'{dev(DEV_TML_RD)}', V: DEV_TML_RD},
                        ],
                        # value=DEV_TML_S  # Dev only, for fast testing
                    )
                ]),
            ]),

            html.Div(className=CNM_MNBD, children=[
                html.Div(id=ID_DIV_PLTS, children=[
                    self.get_fig_layout(idx) for idx in self.idxs_fig
                ])
            ])
        ])

    def get_fig_layout(self, idx):
        return html.Div(
            className=CNM_DIV_LD, children=[
                # All figure data maintained inside layout variable
                dcc.Store(id=m_id(ID_STOR_D_RNG, idx), data=self.curr_plot.D_RNG_INIT),

                html.Div(className=CNM_DIV_LDNM, children=[
                    html.P(self.curr_recr.lead_nms[idx], className=CNM_LD)
                ]),

                html.Div(className=CNM_DIV_TMB, children=[
                    dcc.Graph(
                        id=m_id(ID_TMB, idx), className=CNM_TMB,
                        figure=self.get_thumb_fig(idx)
                    )
                ]),

                html.Div(className=CNM_DIV_FIG, children=[
                    html.Div(className=ID_DIV_FIG_OPN, children=[
                        html.Div(
                            html.Button(id=m_id(ID_BTN_FIXY, idx), className=CNM_BTN, n_clicks=0, children=[
                                html.I(id=m_id(ID_IC_FIXY, idx), className=CNM_IC_LKO)
                            ])),
                    ]),
                    dcc.Graph(
                        id=m_id(ID_GRA, idx), className=CNM_GRA, config=CONF,
                        figure=self.get_lead_fig(idx, self.curr_plot.D_RNG_INIT)
                    )
                ])
            ])

    def _set_callbacks(self):
        self.app.callback(
            [Output(ID_IC_OPN, CNM),
             Output(ID_DIV_OPN, CNM)],
            Input(ID_BTN_OPN, NC)
        )(self.update_div_options)

        self.app.callback(
            Output(ID_DPD_LD_TEMPL, 'disabled'),
            Input(ID_DPD_RECR, V)
        )(self.set_record)

        self.app.callback(
            Output(ID_DIV_PLTS, C),
            Input(ID_DPD_LD_TEMPL, V)
        )(self._load_figs)

        self.app.callback(
            [Output(mch(ID_GRA), F),
             Output(mch(ID_TMB), F)],  # Dummy figure, change its range just to change how the RangeSlider looks
            [Input(mch(ID_GRA), 'relayoutData'),
             Input(mch(ID_TMB), 'relayoutData'),
             Input(mch(ID_BTN_FIXY), NC)],
            [State(mch(ID_STOR_D_RNG), D),
             State(mch(ID_GRA), F),
             State(mch(ID_TMB), F),
             State(mch(ID_GRA), 'id')],
            prevent_initial_call=True
        )(self.update_figure)

        self.app.callback(
            Output(mch(ID_IC_FIXY), CNM),
            Input(mch(ID_BTN_FIXY), NC)
        )(self.update_fix_yaxis_icon)

    def set_record(self, recr_nm):
        """Current record selected to display. Previous record data overridden """
        if recr_nm is None:
            return True
        else:
            self.curr_recr = EcgRecord(DATA_PATH.joinpath(recr_nm))
            self.curr_plot = EcgPlot(self.curr_recr, self)  # A `plot` serves a record
            return False

    def _load_figs(self, key_templ):
        """Set up multiple figures in the APP, original figures shown overridden """
        self.idxs_fig = self.LD_TEMPL[key_templ] if key_templ is not None else []
        return [self.get_fig_layout(idx) for idx in self.idxs_fig]

    @staticmethod
    def update_div_options(n_clicks):
        if n_clicks % 2 == 0:
            return join(CNM_IC_BR, ANM_BTN_OPN_ROTE), join(ANM_DIV_OPN_EXPW, ANM_OPQY)
        else:
            return join(CNM_IC_BR, ANM_BTN_OPN_ROTS), join(ANM_DIV_OPN_CLPW, ANM_OPQN)

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

    def get_thumb_fig(self, idx_lead):
        """
        Plot across the entire channel

        :return: The figure dummy used for global thumbnail preview
        """
        return self.curr_plot.get_thumb_fig(idx_lead)

    def get_lead_xy_vals(self, idx_lead, x_display_range):
        strt, end = x_display_range
        # determine if optimization is needed for large sample_range
        return self.curr_plot.get_xy_vals(idx_lead, strt, end)

    @staticmethod
    def get_last_changed_id():
        """Only 1 input change is needed each time
        :return String representation, caller would check for substring
        """
        return [p['prop_id'] for p in dash.callback_context.triggered][0]

    def update_figure(self, layout_fig, layout_tmb, n_clicks, disp_rng, fig_gra, fig_tmb, id_d_fig):
        """ Update plot in a single call to avoid unnecessary updates, at a point in time, only 1 property change

        :param layout_fig: RelayoutData of actual plot
        :param layout_tmb: RelayoutData of global preview
        :param n_clicks: Number of clicks for the Fix Yaxis button
        :param disp_rng: Internal synchronized display range
        :param fig_gra: Graph object dictionary of actual plot
        :param fig_tmb: Graph object dictionary of global preview
        :param id_d_fig: Pattern matching ID, tells which lead/channel changed
        """
        changed_id = self.get_last_changed_id()
        if ID_GRA in changed_id:  # RelayoutData changed
            if layout_fig is not None and self.ui.KEY_X_S in layout_fig:
                x, y = self.get_lead_xy_vals(id_d_fig[I], self.ui.get_display_range(fig_gra['layout'])[0])
                fig_gra[D][0]['x'] = x  # First (and only) plot/figure on the graph
                fig_gra[D][0]['y'] = y
                fig_tmb['layout']['xaxis']['range'] = fig_gra['layout']['xaxis']['range']
        elif ID_TMB in changed_id:  # Changes in thumbnail figure have to be range change
            x, y = self.get_lead_xy_vals(id_d_fig[I], self.ui.get_x_display_range(fig_tmb['layout']))
            fig_gra[D][0]['x'] = x
            fig_gra[D][0]['y'] = y
            fig_gra['layout']['xaxis']['range'] = fig_tmb['layout']['xaxis']['range']
        elif ID_BTN_FIXY in changed_id:
            fig_gra['layout']['yaxis']['fixedrange'] = n_clicks % 2 == 1
        return fig_gra, fig_tmb

    @staticmethod
    def update_fix_yaxis_icon(n_clicks):
        if n_clicks % 2 == 0:  # Init with yaxis unlocked
            return CNM_IC_LKO
        else:
            return CNM_IC_LK

    @staticmethod
    def example():
        ecg_app = EcgApp(__name__)
        ecg_app.app.title = "Example run"
        return ecg_app

