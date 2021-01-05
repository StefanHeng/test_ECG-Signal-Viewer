import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL

import plotly.graph_objs as go

import concurrent.futures
import time
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
ID_FD_TMB = 'fade_graph-thumbnail'
ID_FD_MN = 'fade_body-main'
CNM_MNBD = 'body_main'
ID_STOR_IDXS_LD = 'store_idxs_lead'

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
ID_STOR_D_RNG = 'store_display_range'  # Contains dictionary of each display range
ID_INTVL = 'interval'
ID_BTN_LD_RMV = 'btn_lead-remove'
CNM_IC_RMV = 'fas fa-minus'

ID_DIV_ADD = 'div_add'
ID_BTN_ADD = 'btn_add'
ID_IC_ADD = 'ic_add'
CNM_IC_ADD = 'fas fa-plus'

ID_MD_ADD = 'modal_add'
ID_MDHD_ADD = 'modal-header_add'
CNM_MDTT = 'modal_title'
CNM_ADD_LD = 'title_add-lead'
TXT_ADD_LD = 'Add a lead/channel: '
ID_BTN_MD_CLS = 'btn_modal-close'
CNM_IC_MD_CLS = 'fas fa-times'
ID_MDBD_ADD = 'modal-body_add'
ID_DIV_MD_ADD = 'div_modal-add'

CNM_BTS_LST = 'list-group'  # For Bootstrap CSS
CNM_BTS_LST_ITM = 'list-group-item list-group-item-action'
ID_STOR_IDX_ADD = 'store_lead-idx-add'  # Current index of lead to add to layout
ID_RDO_LD_ADD = 'radio-group_lead-add'
CNM_RDO_ITM_IPT = 'input_null'
ID_GRP_LD_ADD = 'list-group_lead-add'
ID_ITM_LD_ADD = 'list-item_lead-add'

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
CNM_BTN_FIG_OPN = 'btn_fig-options'
ID_BTN_FIXY = 'btn_fix_yaxis'
ID_IC_FIXY = 'ic_fix_yaxis'
CNM_IC_LK = 'fas fa-lock'  # Font Awesome
CNM_IC_LKO = 'fas fa-lock-open'
ID_STOR_IS_FIXY = 'id_is_yaxis_fixed'

# Syntactic sugar
T = 'type'  # For Dash pattern matching callbacks
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


def all_(id_str):
    return {T: id_str, I: ALL}


def join(*class_nms):  # For Dash className
    """Join string arguments into whitespace-separated single string """
    return ' '.join(class_nms)


DEV_TML_S = 'single -> 1: I'
DEV_TML_RG = 'range(8) -> [1, 8]'
DEV_TML_RD = 'rand -> [7, 6, 4, 17, 36]'


class EcgApp:
    """Handles the Dash web app, interface with potentially multiple records

    Encapsulates all UI interactions including HTML layout, callbacks
    """

    LD_TEMPL = {
        # Arbitrary, for testing only, users should spawn all the leads via UI
        DEV_TML_S: [0],
        DEV_TML_RG: list(range(8)),
        DEV_TML_RD: [6, 5, 3, 16, 35]
    }

    MAX_NUM_LD = 8

    def __init__(self, app_name):
        self.curr_rec = None  # Current record
        self.curr_plot = None
        self.idxs_lead = []
        self.curr_disp_rng = EcgPlot.DISP_RNG_INIT
        self.fig_tmb = None

        self.app_name = app_name  # No human-readable meaning, name passed into Dash object
        self.app = dash.Dash(self.app_name, external_stylesheets=[
            FA_CSS_LNK
        ])
        self.app.layout = self._set_layout()
        self._set_callbacks()
        self.ui = EcgUi(self)

    def run(self, debug=False):
        self.app.run_server(debug=debug)

    def _set_layout(self):
        return html.Div([
            html.Div(className=CNM_HD, children=[
                html.Button(id=ID_BTN_OPN, className=CNM_BTN, n_clicks=0, children=[
                    html.I(id=ID_IC_OPN, className=CNM_IC_BR)
                ]),

                html.H1(TXT_HD, className=CNM_HDTT),

                html.Button(id=ID_BTN_ADD, className=CNM_BTN, n_clicks=0, children=[
                    html.I(id=ID_IC_ADD, className=CNM_IC_ADD)
                ]),
            ]),

            html.Div(id=ID_BBX_DIV_OPN, children=[
                html.Div(id=ID_DIV_OPN, children=[
                    dcc.Dropdown(
                        id=ID_DPD_RECR, className=CNM_MY_DPD, placeholder='Select patient record file',
                        options=[{L: f'{dev(record_nm)}', V: record_nm}],
                        # value=record_nm
                    ),
                    dcc.Dropdown(
                        id=ID_DPD_LD_TEMPL, className=CNM_MY_DPD, disabled=True,
                        placeholder='Select lead/channel template',
                        options=[
                            {L: f'{dev(DEV_TML_S)}', V: DEV_TML_S},
                            {L: f'{dev(DEV_TML_RG)}', V: DEV_TML_RG},
                            {L: f'{dev(DEV_TML_RD)}', V: DEV_TML_RD},
                        ],
                        # value=DEV_TML_S  # Dev only, for fast testing
                    )
                ]),
            ]),

            # dcc.Store(id=ID_STOR_IDXS_LD, data=[]),
            dbc.Fade(id=ID_FD_MN, is_in=True, children=[
                html.Div(className=CNM_MNBD, children=[
                    html.Div(className=CNM_DIV_TMB, children=[
                        dcc.Graph(  # Dummy figure, change its range just to change how the RangeSlider looks
                            # Need a dummy for unknown reason so that Dash loads the layout
                            id=ID_TMB, className=CNM_TMB, figure=go.Figure()
                        )
                    ]),
                    html.Div(id=ID_DIV_PLTS, children=[  # Which is empty list on init
                        self.get_fig_layout(idx) for idx in self.idxs_lead
                    ])
                ])
            ]),

            dbc.Modal(id=ID_MD_ADD, centered=True, is_open=False, scrollable=True, children=[
                dbc.ModalHeader(id=ID_MDHD_ADD, children=[
                    html.H5(TXT_ADD_LD, className=CNM_ADD_LD),
                    html.Button(id=ID_BTN_MD_CLS, className=CNM_BTN, n_clicks=0, children=[
                        html.I(className=CNM_IC_MD_CLS)
                    ])
                ]),
                dbc.ModalBody(id=ID_MDBD_ADD, children=[
                    # dbc.RadioItems(id=ID_RDO_LD_ADD, className=CNM_BTS_LST,
                    #                labelClassName=CNM_BTS_LST_ITM, inputClassName=CNM_RDO_ITM_IPT)
                    dbc.ListGroup(id=ID_GRP_LD_ADD)
                ])
            ])
        ])

    def get_fig_layout(self, idx):
        return html.Div(
            className=CNM_DIV_LD, children=[
                # All figure data maintained inside layout variable
                # dcc.Store(id=m_id(ID_STOR_D_RNG, idx), data=self.curr_plot.D_RNG_INIT),

                html.Div(className=CNM_DIV_LDNM, children=[
                    html.P(self.curr_rec.lead_nms[idx], className=CNM_LD),
                    html.Button(id=m_id(ID_BTN_LD_RMV, idx), className=CNM_BTN, n_clicks=0, children=[
                        html.I(className=CNM_IC_RMV)
                    ])
                ]),

                html.Div(className=CNM_DIV_FIG, children=[
                    html.Div(className=ID_DIV_FIG_OPN, children=[
                        html.Div(
                            html.Button(id=m_id(ID_BTN_FIXY, idx), className=join(CNM_BTN, CNM_BTN_FIG_OPN),
                                        n_clicks=0, children=[
                                    html.I(id=m_id(ID_IC_FIXY, idx), className=CNM_IC_LKO)
                                ])),
                    ]),
                    dcc.Graph(
                        id=m_id(ID_GRA, idx), className=CNM_GRA, config=CONF,
                        figure=self.get_lead_fig(idx, self.curr_disp_rng)
                    )
                ])
            ])

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

    def get_lead_xy_vals(self, idx_lead, x_display_range):
        strt, end = x_display_range
        # determine if optimization is needed for large sample_range
        return self.curr_plot.get_xy_vals(idx_lead, strt, end)

    def _set_callbacks(self):
        self.app.callback(
            [Output(ID_IC_OPN, CNM),
             Output(ID_DIV_OPN, CNM)],
            Input(ID_BTN_OPN, NC)
        )(self.toggle_div_options)

        self.app.callback(
            [Output(ID_DPD_LD_TEMPL, 'disabled'),
             Output(ID_BTN_ADD, 'disabled')],
            Input(ID_DPD_RECR, V)
        )(self.toggle_disable)

        self.app.callback(
            Output(ID_FD_MN, 'is_in'),
            [Input(ID_DPD_LD_TEMPL, V),
             Input(all_(ID_ITM_LD_ADD), NC)]
        )(self.toggle_fade)

        self.app.callback(
            # To invoke changes in global preview add trace below, without having to join all 3 functions into 1
            [Output(ID_DIV_PLTS, C),
             Output(ID_GRP_LD_ADD, C),
             Output(all_(ID_ITM_LD_ADD), 'disabled'),
             Output(all_(ID_GRA), F),
             Output(ID_TMB, F)],
            [Input(ID_DPD_RECR, V),
             Input(ID_DPD_LD_TEMPL, V),
             Input(all_(ID_GRA), 'relayoutData'),
             Input(ID_TMB, 'relayoutData'),
             Input(all_(ID_BTN_FIXY), NC),
             Input(all_(ID_ITM_LD_ADD), NC),
             Input(all_(ID_BTN_LD_RMV), NC)],
            [State(ID_DIV_PLTS, C),
             State(ID_GRP_LD_ADD, C),
             State(all_(ID_ITM_LD_ADD), 'disabled'),
             State(all_(ID_GRA), F),
             State(ID_TMB, F)],
            prevent_initial_call=True
        )(self.update_template_dropdown_add_options_lead_layout_figures)

        self.app.callback(
            Output(ID_MD_ADD, 'is_open'),
            [Input(ID_BTN_ADD, NC),
             Input(ID_BTN_MD_CLS, NC)],
            [State(ID_MD_ADD, 'is_open')],
            prevent_initial_call=True
        )(self.toggle_modal)

        self.app.callback(
            Output(mch(ID_IC_FIXY), CNM),
            Input(mch(ID_BTN_FIXY), NC)
        )(self.update_fix_yaxis_icon)

    @staticmethod
    def get_last_changed_id_property():
        """Only 1 input change is needed each time
        :return String representation, caller would check for substring
        """
        return [p['prop_id'] for p in dash.callback_context.triggered][0]

    @staticmethod
    def toggle_div_options(n_clicks):
        """ Animation on global options setting """
        if n_clicks % 2 == 0:
            return join(CNM_IC_BR, ANM_BTN_OPN_ROTE), join(ANM_DIV_OPN_EXPW, ANM_OPQY)
        else:
            return join(CNM_IC_BR, ANM_BTN_OPN_ROTS), join(ANM_DIV_OPN_CLPW, ANM_OPQN)

    @staticmethod
    def toggle_disable(rec_nm):
        return (False, False) if rec_nm is not None else (True, True)

    @staticmethod
    def toggle_fade(template, ns_clicks_add):
        if template is not None:
            return True
        for nc in ns_clicks_add:
            if nc != 0:
                return True
        return False

    def update_template_dropdown_add_options_lead_layout_figures(
            self, rec_nm, template, layouts_fig, layout_tmb, ns_clicks, ns_clicks_add, ns_clicks_remove,
            plots, items_lead_add, disables_lead_add, figs_gra, fig_tmb):
        """Display lead figures based on current record and template selected, and based on lead selection in modal

        Initializes lead selections

        # Inputs
        :param rec_nm: Name of record selected on dropdown
        :param template: Name of template selected on dropdown
        # :param idx_lead_selected: Index of changed lead

        :param layouts_fig: RelayoutData of actual plot
        :param layout_tmb: RelayoutData of global preview
        :param ns_clicks: Number of clicks for fix-yaxis button
        :param ns_clicks_add: Number of clicks for add lead ListGroup item
        :param ns_clicks_remove: Number of clicks for remove button

        # States
        :param plots: Div list of of lead currently on plot
        :param items_lead_add: Layout of all add-lead items
        :param disables_lead_add: List of disable boolean states for the add-lead items

        :param figs_gra: Graph object dictionary of actual plot
        :param fig_tmb: Graph object dictionary of global preview

        .. note:: Previous record and figure overridden
        .. note:: Selections in modal are disabled if corresponding lead is shown
        """
        # Shared output must be in a single function call per Dash callback
        # => Forced to update in a single function call
        changed_id_property = self.get_last_changed_id_property()
        changed_id = self.ui.get_id(changed_id_property)
        # print(changed_id, changed_id_property)
        if ID_DPD_RECR == changed_id:
            if rec_nm is not None:
                self.curr_rec = EcgRecord(DATA_PATH.joinpath(rec_nm))
                self.curr_plot = EcgPlot(self.curr_rec, self)  # A `plot` serves a record
                # An empty preview and hidden, see `EcgPlot.Thumbnail`
                self.fig_tmb = EcgPlot.Thumbnail(self.curr_rec, self.curr_plot)
                fig_tmb = self.fig_tmb.fig
                # Must generate selections now, for users could not select a template, and customize lead by single add
                # Cannot separate into a new function, cos need to make sure a curr_rec is set first
                items_lead_add = [
                    dbc.ListGroupItem(id=m_id(ID_ITM_LD_ADD, idx), action=True, n_clicks=0, children=f'{idx + 1}: {nm}')
                    for idx, nm in enumerate(self.curr_rec.lead_nms)
                ]
        elif ID_DPD_LD_TEMPL == changed_id:
            if template is not None:
                self.idxs_lead = self.LD_TEMPL[template]
                plots = [self.get_fig_layout(idx) for idx in self.idxs_lead]
                # Override for any template change could happen before
                # Linear, more efficient than checking index in `self.idxs_lead`
                disables_lead_add = [False for i in disables_lead_add]
                for idx in self.idxs_lead:
                    disables_lead_add[idx] = True
                fig_tmb = self.fig_tmb.add_trace(self.idxs_lead, override=True)
            else:  # Reset layout
                self.idxs_lead = []
                plots = []
                # All options are not disabled
                items_lead_add = [
                    dbc.ListGroupItem(id=m_id(ID_ITM_LD_ADD, idx), action=True, n_clicks=0, children=f'{idx + 1}: {nm}')
                    for idx, nm in enumerate(self.curr_rec.lead_nms)
                ]
                disables_lead_add = [False for i in disables_lead_add]
                # figs_gra = []  # For same reason below, the remove button case
                # Basically removes all trace without adding
                fig_tmb = self.fig_tmb.add_trace([], override=True)
        elif ID_ITM_LD_ADD == changed_id:  # A new lead layout should be appended, due to click in modal
            idx_changed = self.ui.get_pattern_match_index(changed_id_property)
            self.idxs_lead.append(idx_changed)
            plots.append(self.get_fig_layout(idx_changed))
            disables_lead_add[idx_changed] = True
            fig_tmb = self.fig_tmb.add_trace([idx_changed], override=False)

        elif ID_GRA == changed_id:  # RelayoutData changed, graph has pattern matched ID
            idx_changed = self.ui.get_pattern_match_index(changed_id_property)
            idx_idx_changed = self._get_fig_index_by_index(idx_changed)
            if layouts_fig is not None and self.ui.KEY_X_S in layouts_fig[idx_idx_changed]:
                self.curr_disp_rng[0] = self.ui.get_x_display_range(figs_gra[idx_idx_changed]['layout'])
                # yaxis_rng_ori = self.ui.get_y_display_range(layouts_fig[idx_idx_changed])  # Upon user request
                yaxis_rng_ori = figs_gra[idx_idx_changed]['layout']['yaxis']['range']
                fig_tmb['layout']['xaxis']['range'] = x_layout_range = \
                    self.ui.get_x_layout_range(layouts_fig[idx_idx_changed])
                self._update_lead_figures(figs_gra, x_layout_range)
                figs_gra[idx_idx_changed]['layout']['yaxis']['range'] = yaxis_rng_ori
        elif ID_TMB == changed_id:  # Changes in thumbnail figure have to be range change
            # Workaround: At first app start, ID_TMB is in changed_id for unknown reason
            if 'xaxis' in fig_tmb['layout']:
                self.curr_disp_rng[0] = self.ui.get_x_display_range(fig_tmb['layout'])
                self._update_lead_figures(figs_gra, fig_tmb['layout']['xaxis']['range'])
        # elif ID_BTN_FIXY == changed_id:
        #     figs_gra['layout']['yaxis']['fixedrange'] = ns_clicks % 2 == 1
        elif ID_BTN_LD_RMV == changed_id:
            idx_changed = self.ui.get_pattern_match_index(changed_id_property)
            idx_idx_changed = self._get_fig_index_by_index(idx_changed)
            del self.idxs_lead[idx_idx_changed]
            del plots[idx_idx_changed]
            disables_lead_add[idx_changed] = False
            # Surprisingly when I have the line below, Dash gives weird exception, instead of not having this line
            # del figs_gra[idx_idx_changed]'
        return plots, items_lead_add, disables_lead_add, figs_gra, fig_tmb

    def _update_lead_figures(self, figs_gra, x_layout_range):
        strt, end = self.curr_disp_rng[0]
        sample_factor = self.curr_plot.get_sample_factor(strt, end)
        x_vals = self.curr_plot.get_x_vals(strt, end, sample_factor)
        args = [(figs_gra, idx_idx, idx_lead, strt, end, sample_factor)
                for idx_idx, idx_lead in enumerate(self.idxs_lead)]
        # Multi-threading for mainly IO
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.MAX_NUM_LD) as executor:
            executor.map(lambda p: self._set_y_vals(*p), args)

        for idx_idx in range(len(self.idxs_lead)):  # Lines up with number of figures plotted
            # Short execution time, no need to multi-process
            figs_gra[idx_idx][D][0]['x'] = x_vals
            figs_gra[idx_idx]['layout']['xaxis']['range'] = x_layout_range

    def _set_y_vals(self, figs_gra, idx_idx, idx_lead, strt, end, sample_factor):
        y_vals = self.curr_plot.get_y_vals(idx_lead, strt, end, sample_factor)
        figs_gra[idx_idx][D][0]['y'] = y_vals
        figs_gra[idx_idx]['layout']['yaxis']['range'] = self.ui.get_ignore_noise_range(y_vals)

    @staticmethod
    def toggle_modal(n_clicks_add, n_clicks_close, is_open):
        return not is_open

    def _get_fig_index_by_index(self, index):
        """ Gets the index of the index stored in `idxs_fig`

        One-to-one correspondence with the order of children figures

        Precondition: index is a member of `idxs_fig`
        """
        for i, idx in enumerate(self.idxs_lead):
            if idx == index:
                return i
        return None  # Not intended to reach here

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

