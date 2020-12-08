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
                        ]
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
            [Output(mch(ID_STOR_D_RNG), D),
             Output(mch(ID_TMB), F)],  # Dummy figure, change its range just to change how the RangeSlider looks
            [Input(mch(ID_GRA), 'relayoutData'),
             Input(mch(ID_TMB), 'relayoutData')],
            [State(mch(ID_STOR_D_RNG), D),
             State(mch(ID_TMB), F)]
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
            Input(mch(ID_BTN_FIXY), NC)
        )(self.update_fix_yaxis_icon)
        self.app.callback(
            Output(mch(ID_GRA), F),
            [Input(mch(ID_STOR_D_RNG), D),
             Input(mch(ID_BTN_FIXY), NC)],
            [State(mch(ID_GRA), F),
             State(mch(ID_GRA), 'id')]
        )(self.update_figure)
        self.app.callback(
            [Output(ID_IC_OPN, CNM),
             Output(ID_DIV_OPN, CNM)],
            Input(ID_BTN_OPN, NC)
        )(self.update_div_options)

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

    def get_lead_xy_vals(self, idx_lead, display_range):
        strt, end = display_range[0]
        # determine if optimization is needed for large sample_range
        return self.curr_plot.get_xy_vals(idx_lead, strt, end)

    @staticmethod
    def get_changed_ids():
        """Only 1 input change is needed each time """
        return [p['prop_id'] for p in dash.callback_context.triggered][0]

    def update_lims(self, r_data_fig, r_data_tmb, d_range, fig_tmb):
        # return self.ui.to_sample_lim(r_data_fig, d_range)
        changed_id = self.get_changed_ids()
        # print(f'in update lim')
        # print('all ids changed', [p['prop_id'] for p in dash.callback_context.triggered])
        # print(f'relayout for thumb: {r_data_tmb}')
        if ID_GRA in changed_id:
            fig_tmb['layout']['xaxis']['range'] = self.ui.relayout_data_update_xaxis_range(
                r_data_fig, fig_tmb['layout']['xaxis']['range'])
            # print('graph updated: ', fig_tmb['layout']['xaxis']['range'])
            # if self.ui.KEY_X_S in r_data_fig:
            #     x_strt = r_data_fig[self.ui.KEY_X_S]
            #     x_end = r_data_fig[self.ui.KEY_X_E]
            #     fig_tmb['layout']['xaxis']['range'] = [x_strt, x_end]
                # print(f'graph data changed with layout and x_strt {x_strt} and x_end {x_end}')
            return self.ui.relayout_data_to_display_range(r_data_fig, d_range), fig_tmb
        elif ID_TMB in changed_id:
            d_range = self.ui.relayout_data_update_display_range(r_data_tmb, d_range)
            # print('preview updated: ', fig_tmb['layout']['xaxis']['range'], f'and d_range[0] is {d_range[0]}')
            return d_range, fig_tmb
        else:
            return d_range, fig_tmb

    def update_figure(self, d_range, n_clicks, fig, id_d):
        changed_id = self.get_changed_ids()
        # print(f'in update fig')
        # print('all ids changed', [p['prop_id'] for p in dash.callback_context.triggered])
        if ID_STOR_D_RNG in changed_id:  # Check substring
            # print('channel fig should update')
            x, y = self.get_lead_xy_vals(id_d[I], d_range)
            # xn = x.to_numpy()
            # print(f'x data range is strt: {x[0]}, end: {xn[-1]}')
            # print(f'stored d_range is {self.curr_recr.sample_count_to_time_str(d_range[0][0]),}, {self.curr_recr.sample_count_to_time_str(d_range[0][1])}')

            fig[D][0]['x'] = x  # First plot/figure on the graph
            fig[D][0]['y'] = y
            fig['layout']['xaxis']['range'] = [
                self.curr_recr.sample_count_to_time_str(d_range[0][0]),
                self.curr_recr.sample_count_to_time_str(d_range[0][1])
            ]
        elif ID_BTN_FIXY in changed_id:
            fig['layout']['yaxis']['fixedrange'] = n_clicks % 2 == 1
        return fig

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
