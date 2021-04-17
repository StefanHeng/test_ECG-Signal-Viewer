import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash_extensions import Download
from dash.exceptions import PreventUpdate

import plotly.graph_objs as go

import pandas as pd

# import time
from datetime import datetime  # , timedelta
from copy import deepcopy
from bisect import bisect_left
import concurrent.futures
# from typing import List, Set, Dict, Tuple, Optional
from typing import List, Dict

from icecream import ic

from data_link import *
from dev_helper import *

from ecg_app_defns import *
from ecg_record import EcgRecord
from ecg_plot import EcgPlot
from ecg_ui import EcgUi
from ecg_comment import EcgComment
from ecg_export import EcgExport


def __get_curr_time():
    return datetime.now().strftime('%H:%M:%S.%f')[:-3]


def t_stamp():
    return '%s |> ' % __get_curr_time()


ic.configureOutput(prefix=t_stamp)


INF = float('inf')


class EcgApp:
    """Handles the Dash web app, interface with potentially multiple records

    Encapsulates all UI interactions including HTML layout, callbacks
    """
    MAX_NUM_LD = 12
    MAX_TXTA_RW = 10  # Maximum number of `rows` for comment textarea
    MIN_TXTA_RW = 4

    HT_LDS = 85  # Height that the leads take on, as a percentage of view window size

    LD_TEMPL = {
        # Arbitrary, for testing only, users should spawn all the leads via UI
        DEV_TML_S: [0],
        DEV_TML_RG: list(range(8)),
        DEV_TML_RD: [6, 5, 3, 16, 35],
        DEV_TML_RG2: list(range(12))
    }

    MV_OFST_TIMES = {  # On how much time does advance and nudge operations move
        ID_BTN_ADV_BK: pd.Timedelta(-2, unit='m'),
        ID_BTN_MV_BK: pd.Timedelta(-10, unit='s'),
        ID_BTN_MV_FW: pd.Timedelta(10, unit='s'),
        ID_BTN_ADV_FW: pd.Timedelta(2, unit='m')
    }

    MAX_PRV_LEN = 30  # Maximum number of characters for the comment preview

    def __init__(self, app_name):
        self.rec = None  # Current record
        self.plt = None
        self.ui = EcgUi(None)
        self.cmts = EcgComment(None)
        self.exp = EcgExport()
        self.idxs_lead = []
        self.disp_rng = EcgPlot.DISP_RNG_INIT
        self.fig_tmb = None
        self._yaxis_fixed = False
        self._marking_on = False
        # self._shapes = []  # Current shapes drawn, to be synchronized across new leads added
        self.idx_ann_clicked = None
        self.ks_cmts = None  # Keys for internal comment data lookup, by order of each comment on display

        self.move_offset_counts = None  # Runtime optimization, semi-constants dependent to record
        self.no_update_add_opns = None

        self.app_name = app_name  # No human-readable meaning, name passed into Dash object
        self.app = dash.Dash(self.app_name, external_stylesheets=[
            FA_CSS_LNK,
            dbc.themes.LUX
        ])

        def _set_layout():
            return html.Div([
                # Header
                html.Div(className=CNM_HD, children=[
                    html.Button(id=ID_BTN_OPN, className=CNM_BTN, n_clicks=0, children=[
                        html.I(id=ID_IC_OPN, className=CNM_IC_BR)
                    ]),

                    html.H1(TXT_HD, id=ID_HDTT),

                    html.Button(id=ID_BTN_ADD, className=CNM_BTN, disabled=True, n_clicks=0, children=[
                        html.I(id=ID_IC_ADD, className=CNM_IC_ADD)
                    ]),
                    html.Button(id=ID_BTN_EXP, className=CNM_BTN, disabled=True, n_clicks=0, children=[
                        html.I(className=CNM_IC_EXP)
                    ]),
                    # When target is disabled, ToolTip won't show
                    dbc.Tooltip(target=ID_BTN_ADD, hide_arrow=False, placement=TTP_PLCM, offset=TTP_OFST,
                                children='Add a lead channel'),
                    dbc.Tooltip(target=ID_BTN_EXP, hide_arrow=False, placement=TTP_PLCM, offset=TTP_OFST,
                                children='Export to csv'),
                    Download(id=ID_DLD_CSV),

                    html.Div(id=ID_DIV_PLT_CTRL, children=[
                        html.Button(id=ID_BTN_ADV_BK, className=join(CNM_BTN, CNM_BTN_FIG_OPN), disabled=True,
                                    children=[
                                        html.I(className=CNM_ADV_BK)
                                    ]),
                        html.Button(id=ID_BTN_MV_BK, className=join(CNM_BTN, CNM_BTN_FIG_OPN), disabled=True, children=[
                            html.I(className=CNM_MV_BK)
                        ]),
                        html.Button(id=ID_BTN_FIXY, className=join(CNM_BTN, CNM_BTN_FIG_OPN), disabled=False,
                                    n_clicks=0,
                                    children=[
                                        html.I(id=ID_IC_FIXY, className=CNM_IC_LKO)
                                    ]),
                        html.Button(id=ID_BTN_MV_FW, className=join(CNM_BTN, CNM_BTN_FIG_OPN), disabled=True, children=[
                            html.I(className=CNM_MV_FW)
                        ]),
                        html.Button(id=ID_BTN_ADV_FW, className=join(CNM_BTN, CNM_BTN_FIG_OPN), disabled=True,
                                    children=[
                                        html.I(className=CNM_ADV_FW)
                                    ]),
                        html.Button(id=ID_BTN_TG_TG, className=join(CNM_BTN, CNM_BTN_FIG_OPN), disabled=False,
                                    n_clicks=0,
                                    children=[
                                        html.I(id=ID_IC_TG_TG, className=join(CNM_TG_TG, ANM_BTN_TG_TG_ROTS))
                                    ]),
                        html.Button(id=ID_BTN_CLP_CLR, className=join(CNM_BTN, CNM_BTN_FIG_OPN), disabled=True,
                                    children=[
                                        html.I(className=CNM_CLP_CLR)
                                    ]),
                    ]),
                    dbc.Tooltip(target=ID_BTN_ADV_BK, hide_arrow=False, placement=TTP_PLCM_PLT_CTRL, offset=TTP_OFST,
                                delay=TTP_DL, children='Advance backward'),
                    dbc.Tooltip(target=ID_BTN_MV_BK, hide_arrow=False, placement=TTP_PLCM_PLT_CTRL, offset=TTP_OFST,
                                delay=TTP_DL, children='Nudge backward'),
                    dbc.Tooltip(target=ID_BTN_FIXY, hide_arrow=False, placement=TTP_PLCM_PLT_CTRL, offset=TTP_OFST,
                                delay=TTP_DL, children='Fix y-axis'),
                    dbc.Tooltip(target=ID_BTN_MV_FW, hide_arrow=False, placement=TTP_PLCM_PLT_CTRL, offset=TTP_OFST,
                                delay=TTP_DL, children='Nudge forward'),
                    dbc.Tooltip(target=ID_BTN_ADV_FW, hide_arrow=False, placement=TTP_PLCM_PLT_CTRL, offset=TTP_OFST,
                                delay=TTP_DL, children='Advance forward'),
                    dbc.Tooltip(target=ID_BTN_TG_TG, hide_arrow=False, placement=TTP_PLCM_PLT_CTRL, offset=TTP_OFST,
                                delay=TTP_DL, children='Show/Hide markings'),
                    dbc.Tooltip(target=ID_BTN_CLP_CLR, hide_arrow=False, placement=TTP_PLCM_PLT_CTRL, offset=TTP_OFST,
                                delay=TTP_DL, children='Clear caliper measurements'),

                    html.Div(id=ID_DIV_TMLB, children=[
                        html.P(id=ID_TMLB)
                    ])
                ]),

                # Floating dropdown panel
                html.Div(id=ID_BBX_DIV_OPN, children=[
                    html.Div(id=ID_DIV_OPN, children=[
                        # Sets the record, a separate call back function to make sure execution order
                        dcc.Store(id=ID_STOR_REC),
                        dcc.Dropdown(
                            id=ID_DPD_RECR, className=CNM_MY_DPD, placeholder='Select patient record file',
                            options=[{L: f'{dev(record_nm)}', V: record_nm}],
                            # value=record_nm
                        ),
                        dcc.Dropdown(
                            id=ID_DPD_LD_TEMPL, className=CNM_MY_DPD, disabled=True,
                            placeholder='Select lead channel template',
                            options=[
                                {L: f'{dev(DEV_TML_S)}', V: DEV_TML_S},
                                {L: f'{dev(DEV_TML_RD)}', V: DEV_TML_RD},
                                {L: f'{dev(DEV_TML_RG)}', V: DEV_TML_RG},
                                {L: f'{dev(DEV_TML_RG2)}', V: DEV_TML_RG2},
                            ],
                            # value=DEV_TML_S  # Dev only, for fast testing
                        )
                    ]),
                ]),

                dbc.Alert(
                    id=ID_ALT_CMT_SVD, is_open=False, fade=True, duration=1000, dismissable=True, color='success',
                    className=CNM_ALT, children=f'Comment saved',
                ),
                dbc.Fade(id=ID_FD_MN, is_in=False, children=[
                    html.Div(className=CNM_MNBD, children=[
                        html.Div(className=CNM_DIV_TMB, children=[  # Thumbnail graph on top
                            dcc.Graph(  # Dummy figure, change its range just to change how the RangeSlider looks
                                # Need a dummy for unknown reason so that Dash loads the layout
                                id=ID_TMB, className=CNM_TMB, figure=go.Figure()
                            )
                        ]),
                        html.Div(id=ID_DIV_TABS, children=[  # 3 tabs
                            # Tab 1, the lead channels
                            html.Div(id=ID_DIV_PLTS, children=[  # Which is empty list on init
                                self.get_fig_layout(idx) for idx in self.idxs_lead
                            ]),

                            # Tab 2, clickable and editable items, comments and tags
                            html.Div(id=ID_DIV_CMT_TG, className=ANM_DIV_CMT_TG_CLPW, children=[
                                html.Div(id=ID_DIV_CMT_LB),
                                html.Div(id=ID_DIV_CMT_ED, children=[
                                    dbc.Textarea(id=ID_TXTA_CMT, rows=self.MIN_TXTA_RW, disabled=True,
                                                 placeholder='Edit comment to most recent caliper measurement'),
                                    html.Button(id=ID_BTN_CMT_SBM, className=CNM_BTN, disabled=True, children='SAVE'),
                                ]),
                                html.Div(id=ID_DIV_CMT_LST, children=[
                                    dbc.ListGroup(id=ID_GRP_CMT)
                                ]),

                                # Static tag list
                                dcc.Store(id=ID_STOR_TG_IDX),  # Write to layout, triggered by clientside callback
                                # Keep track of number of clicks on tag items, essential for clientside callback
                                dcc.Store(id=ID_STOR_TG_NCS),
                                html.Div(id=ID_DIV_TG, children=[
                                    dbc.ListGroup(id=ID_GRP_TG)
                                ]),
                            ]),

                            # Tab 3, the button to expand/collapse tab 2
                            # It's okay, always enabled, cos if no lead channel on display,
                            # the button is not even visible
                            html.Button(id=ID_BTN_CMT_TG_TG, className=join(CNM_BTN, ANM_BTN_TG_BDR_SH), n_clicks=0,
                                        children=[
                                            html.I(id=ID_IC_CMT_TG_TG, className=CNM_TG_EXP)
                                        ])
                        ])
                    ])
                ]),

                dcc.Store(id=ID_STOR_ADD),
                dcc.Store(id=ID_STOR_RMV),

                dbc.Alert(
                    id=ID_ALT_MAX_LD, is_open=False, fade=True, duration=4000, dismissable=True, color='danger',
                    className=CNM_ALT,
                    children=f'Error: Maximum of {self.MAX_NUM_LD} lead channels supported for display',
                ),
                dbc.Modal(id=ID_MD_ADD, centered=True, is_open=False, scrollable=True, children=[
                    dbc.ModalHeader(id=ID_MDHD_ADD, children=[
                        html.H5(TXT_ADD_LD, className=CNM_ADD_LD),
                        html.Button(id=ID_BTN_MD_CLS, className=CNM_BTN, n_clicks=0, children=[
                            html.I(className=CNM_IC_MD_CLS)
                        ]),
                    ]),
                    dbc.ModalBody(id=ID_MDBD_ADD, children=[
                        dbc.ListGroup(id=ID_GRP_LD_ADD),
                    ]),
                ]),
            ])

        self.app.layout = _set_layout()
        self._set_callbacks()

    def run(self, debug=False):
        self.app.run_server(debug=debug)

    def get_fig_layout(self, idx, tags=None):
        def get_lead_fig(idx_lead, tags=None, shapes=None):
            """
            :param idx_lead: index of lead as stored in .h5 datasets
            :param tags: Tags within display range as stored in `EcgRecord`
            :param shapes: List of current user-drawn shapes

            .. note:: A valid range has values in [0, sum of all samples across the entire ecg_record),
            one-to-one correspondence with time by `sample_rate`

            :return: dictionary that represents a plotly graph
            """
            return self.plt.get_fig(idx_lead, *self.disp_rng[0], tags, shapes, self._yaxis_fixed)

        return dbc.Fade(className=CNM_DIV_FD, is_in=True, children=[
            html.Div(id=m_id(ID_DIV_LD, idx), className=CNM_DIV_LD, children=[
                html.Div(className=CNM_DIV_LDNM, children=[
                    html.P(self.rec.lead_nms[idx], className=CNM_LD),
                    # Workaround wrapper for Tooltip doesn't support pattern-matched id
                    html.Div(id=f'{ID_BTN_LD_RMV_WP}{idx}', children=[
                        html.Button(id=m_id(ID_BTN_LD_RMV, idx), className=CNM_BTN, n_clicks=0, children=[
                            html.I(className=CNM_IC_RMV)
                        ])
                    ]),
                    dbc.Tooltip(target=f'{ID_BTN_LD_RMV_WP}{idx}', hide_arrow=False, placement=TTP_PLCM,
                                offset=TTP_OFST,
                                # delay=dict(show=500, hide=500),
                                children='Remove the lead channel'),
                ]),

                html.Div(className=CNM_DIV_FIG, children=[
                    dcc.Graph(
                        id=m_id(ID_GRA, idx), className=CNM_GRA, config=CONF,
                        figure=get_lead_fig(idx, tags, self._get_all_annotations(self.idx_ann_clicked, idx))
                    )
                ])
            ])
        ])

    # def get_lead_xy_vals(self, idx_lead, x_display_range):
    #     strt, end = x_display_range
    #     # determine if optimization is needed for large sample_range
    #     return self.plt.get_xy_vals(idx_lead, strt, end)

    def _set_callbacks(self):
        self.app.callback(
            [Output(ID_IC_OPN, CNM),
             Output(ID_DIV_OPN, CNM)],
            Input(ID_BTN_OPN, NC)
        )(self.toggle_div_options)

        self.app.callback(
            Output(ID_STOR_REC, D),
            Input(ID_DPD_RECR, V),
            prevent_initial_call=True
        )(self.set_record_init)

        self.app.callback(
            [Output(ID_DPD_LD_TEMPL, DS),
             Output(ID_BTN_ADD, DS)],
            Input(ID_STOR_REC, D),
            prevent_initial_call=True
        )(self.toggle_disable)

        self.app.callback(
            [Output(ID_FD_MN, 'is_in'),
             Output(ID_BTN_ADV_BK, DS),
             Output(ID_BTN_MV_BK, DS),
             # Output(ID_BTN_FIXY, DS),
             Output(ID_BTN_MV_FW, DS),
             Output(ID_BTN_ADV_FW, DS),
             Output(ID_BTN_CLP_CLR, DS)
             # Output(ID_BTN_ANTN_TG, DS)
             ],
            [Input(ID_DPD_LD_TEMPL, V),
             Input(ID_STOR_ADD, D),
             Input(ID_STOR_RMV, D)],
            prevent_initial_call=True
        )(self.toggle_layout_fade)

        self.app.callback(
            Output(ID_GRP_LD_ADD, C),
            Input(ID_STOR_REC, D),
            prevent_initial_call=True
        )(self.set_add_lead_options)

        # Make sure index is updated first before other callbacks update based on `idxs_lead`
        self.app.callback(
            Output(ID_STOR_ADD, D),
            Input(all_(ID_ITM_LD_ADD), NC),
            prevent_initial_call=True
        )(self.update_lead_indices_add)

        self.app.callback(
            Output(ID_STOR_RMV, D),
            Input(all_(ID_BTN_LD_RMV), NC),
            prevent_initial_call=True
        )(self.update_lead_indices_remove)

        self.app.callback(
            Output(all_(ID_DIV_LD), 'style'),
            Input(ID_DIV_PLTS, C),
        )(self.update_lead_height_styles)

        self.app.callback(
            Output(ID_TXTA_CMT, 'rows'),
            Input(ID_TXTA_CMT, 'value'),
            prevent_initial_call=True
        )(self.update_comment_textarea_height)

        self.app.callback(
            [Output(ID_ALT_CMT_SVD, 'is_open'),
             Output(ID_GRP_CMT, C)],
            [Input(ID_DPD_LD_TEMPL, V),
             Input(ID_STOR_ADD, D),
             Input(ID_STOR_RMV, D),
             Input(ID_BTN_CMT_SBM, NC)],
            State(ID_TXTA_CMT, 'value'),
            prevent_initial_call=True
        )(self.update_comments_panel)

        self.app.callback(
            [Output(ID_DIV_PLTS, C),
             Output(all_(ID_ITM_LD_ADD), DS),
             Output(all_(ID_GRA), F),
             Output(ID_TMB, F),
             Output(ID_TMLB, C),  # Updates the time duration label
             Output(ID_DIV_CMT_LB, C),  # Updates the comment range label
             Output(ID_TXTA_CMT, DS),
             Output(ID_BTN_CMT_SBM, DS),
             Output(ID_BTN_EXP, DS),
             Output(ID_STOR_TG_NCS, D)],
            [Input(ID_STOR_REC, D),
             Input(ID_DPD_LD_TEMPL, V),
             Input(all_(ID_GRA), 'relayoutData'),
             Input(ID_TMB, 'relayoutData'),
             Input(ID_BTN_ADV_BK, NC),
             Input(ID_BTN_MV_BK, NC),
             Input(ID_BTN_FIXY, NC),
             Input(ID_BTN_MV_FW, NC),
             Input(ID_BTN_ADV_FW, NC),
             Input(ID_IC_TG_TG, CNM),  # Ensures `_marking_on` is first toggled
             Input(ID_BTN_CLP_CLR, NC),
             Input(ID_STOR_ADD, D),
             Input(ID_STOR_RMV, D),
             Input(ID_STOR_TG_IDX, D),  # Static tag click
             Input(all_(ID_BDG_CMT_TM), NC)],  # Comment timestamp click
            [State(ID_DIV_PLTS, C),
             State(all_(ID_ITM_LD_ADD), DS),
             State(all_(ID_GRA), F),
             State(ID_TMB, F),
             State(ID_STOR_TG_NCS, D)],  # Models the change in number of clicks
            prevent_initial_call=True
        )(self.update_lead_options_disable_layout_figures)

        self.app.callback(
            Output(ID_MD_ADD, 'is_open'),
            [Input(ID_BTN_ADD, NC),
             Input(ID_BTN_MD_CLS, NC)],
            [State(ID_MD_ADD, 'is_open')],
            prevent_initial_call=True
        )(self.toggle_modal)

        self.app.callback(
            Output(ID_ALT_MAX_LD, 'is_open'),
            [Input(ID_STOR_ADD, D),
             Input(ID_DPD_LD_TEMPL, V)],
            State(ID_ALT_MAX_LD, 'is_open'),
            prevent_initial_call=True
        )(self.toggle_max_lead_error)

        self.app.callback(
            Output(ID_IC_FIXY, CNM),
            Input(ID_BTN_FIXY, NC),
            prevent_initial_call=True
        )(self.update_fix_yaxis_icon)

        self.app.callback(
            Output(ID_DLD_CSV, D),
            Input(ID_BTN_EXP, NC),
            prevent_initial_call=True
        )(self.export_csv)

        self.app.callback(
            [Output(ID_DIV_CMT_TG, CNM),
             Output(ID_BTN_CMT_TG_TG, CNM),
             Output(ID_IC_CMT_TG_TG, CNM),
             Output(ID_DIV_PLTS, CNM)],
            Input(ID_BTN_CMT_TG_TG, NC),
            prevent_initial_call=True
        )(self.toggle_tags_n_comments_panel)

        self.app.callback(
            Output(ID_GRP_TG, C),
            Input(ID_STOR_REC, D),
            prevent_initial_call=True
        )(self.get_tags_layout)

        self.app.callback(
            Output(ID_IC_TG_TG, CNM),
            Input(ID_BTN_TG_TG, NC),
            prevent_initial_call=True
        )(self.toggle_show_markings)

        self.app.clientside_callback(
            ClientsideFunction(  # clientside callback for efficiency
                namespace='clientside',
                function_name='update_tag_clicked'
            ),
            Output(ID_STOR_TG_IDX, D),
            Input(all_(ID_ITM_TG), NC),
            State(ID_STOR_TG_NCS, D),
            prevent_initial_call=True
        )

    @staticmethod
    def get_last_changed_id_property():
        """Only 1 input change is needed each time
        :return String representation, caller would check for substring
        """
        return dash.callback_context.triggered[0]['prop_id']

    @staticmethod
    def toggle_div_options(n_clicks):
        """ Animation on global options setting """
        if n_clicks % 2 == 0:
            return join(CNM_IC_BR, ANM_IC_OPN_ROTE), join(ANM_DIV_OPN_EXPW, ANM_OPQY)
        else:
            return join(CNM_IC_BR, ANM_IC_OPN_ROTS), join(ANM_DIV_OPN_CLPW, ANM_OPQN)

    def set_record_init(self, record_name):
        # EcgApp.__print_changed_property('init record')
        if record_name is not None:
            # Makes sure the following attributes are set first before needed
            path = DATA_PATH.joinpath(record_name)
            path_p = CURR.joinpath(f'{path.stem}_preprocessed.hdf5')  # Preprocessed record
            self.rec = EcgRecord(path, path_p)
            self.plt = EcgPlot(self.rec, self)  # A `plot` serves a record
            self.ui = EcgUi(self.rec)
            self.cmts.init(self.rec)
            self.exp.set_record(self.rec, self.cmts)
            # An empty preview and hidden, see `EcgPlot.Thumbnail`
            self.fig_tmb = EcgPlot.Thumbnail(self.rec, self.plt)

            self.move_offset_counts = {k: self.rec.pd_delta_to_count(EcgApp.MV_OFST_TIMES[k])
                                       for k in EcgApp.MV_OFST_TIMES}
            self.no_update_add_opns = [dash.no_update] * self.rec.n_lead
        return record_name

    @staticmethod
    def toggle_disable(rec_nm):
        # EcgApp.__print_changed_property('toggle btn&tpl disable')
        if rec_nm is not None:
            return lst_to_tuple([False] * 2)  # For 2 output properties
        else:
            return lst_to_tuple([True] * 2)

    def toggle_layout_fade(self, template, data_add, data_rmv):
        # EcgApp.__print_changed_property('toggle layout fade')
        if self.ui.get_id(self.get_last_changed_id_property()) == ID_DPD_LD_TEMPL:
            b = template is not None
        else:  # Due to lead add or remove
            b = len(self.idxs_lead) > 0
        return lst_to_tuple([b] + [not b] * 5)

    def set_add_lead_options(self, record_name):
        # EcgApp.__print_changed_property('update add lead options')
        # changed_id_property = self.get_last_changed_id_property()
        # changed_id = self.ui.get_id(changed_id_property)
        if record_name is not None:  # Initialize
            # Must generate selections now, for users could not select a template, and customize lead by single add
            return [
                dbc.ListGroupItem(id=m_id(ID_ITM_LD_ADD, idx), action=True, n_clicks=0, children=f'{idx + 1}: {nm}')
                for idx, nm in enumerate(self.rec.lead_nms)
            ]
        else:
            return None
        # return items_lead_add

    def get_tags_layout(self, record_name):
        if record_name is not None:  # `curr_rec` already loaded
            layout = [dbc.ListGroupItem(className=CNM_TG_BLK, action=True, children=[
                dbc.Badge(id=m_id(ID_ITM_TG, idx), className=CNM_BDG_MY_INT, n_clicks=0,
                          children=self.rec.count_to_str(self.rec.ms_to_count(tm))),
                dbc.Badge(className=CNM_BDG_MY, children=typ),
                html.P(className=CNM_TG_TXT, children=txt)
            ]) for idx, (typ, tm, txt) in enumerate(self.rec.tags)]
            return layout
        else:
            return None

    def update_lead_indices_add(self, ns_clicks_add):
        # EcgApp.__print_changed_property('clicked on add button')
        # Magnitude of n_clicks doesn't really matter, just care about which index clicked
        # The same applies to the remove call back below
        changed_id_property = self.get_last_changed_id_property()
        if changed_id_property != '.':
            idx = self.ui.get_pattern_match_index(changed_id_property)
            # In case of first call when record is set which creates add button children, then n_clicks is actually 0
            if len(self.idxs_lead) >= self.MAX_NUM_LD or ns_clicks_add[idx] == 0:  # Due to element creation
                # Bool for if appending took place
                return False, None  # Can't do prevent update, cos need the callback to trigger max lead error alert
            else:
                self.idxs_lead.append(idx)
                return True, idx
        else:
            raise PreventUpdate

    def update_lead_indices_remove(self, ns_clicks_rmv):
        # EcgApp.__print_changed_property('clicked on remove button')
        changed_id_property = self.get_last_changed_id_property()
        if changed_id_property == '.':  # When button elements are removed from web layout
            raise PreventUpdate
        idx = self.ui.get_pattern_match_index(changed_id_property)
        idx_idx = self._get_fig_index_by_index(idx)
        if ns_clicks_rmv[idx_idx] == 0:  # In case selecting template creates new remove buttons
            raise PreventUpdate
        else:
            # Except from the reason same as add callback above,
            # a lead is always removed cos otherwise there's no div to trigger the button callback
            del self.idxs_lead[idx_idx]
            # Original index in layout, subsequent callback below will remove div from HTML plots
            return idx_idx, idx

    def update_num_lead(self, template, data_add, data_rmv):
        return len(self.idxs_lead)

    def update_lead_height_styles(self, plots):
        num_lead = len(self.idxs_lead)
        if num_lead == 0:  # The layout is hidden anyway
            return [dash.no_update] * num_lead
        else:
            h = f'{int(self.HT_LDS / max(num_lead, 3))}vh'  # So that maximal height is 1/3 of the div
            return [dict(height=h)] * num_lead

    def update_comment_textarea_height(self, txt):
        """ Rough measure based on number of characters and number of line breaks """
        if txt is not None:
            n_ch = len(txt) if txt is not None else 0
            n_ln = txt.count('\n')
            n_row = max(n_ch // 30, n_ln)
            min_bound = max(n_row + 1, self.MIN_TXTA_RW)
            return min(min_bound, self.MAX_TXTA_RW)
        else:
            return self.MIN_TXTA_RW

    def update_comments_panel(self, template, data_add, data_rmv, nc, msg):
        """ On lead channel change, no comment saved, but all previous comments displayed
        """
        id_changed = self.ui.get_id(self.get_last_changed_id_property())
        cmt_saved = False
        if id_changed == ID_BTN_CMT_SBM:
            # There's definitely a mru if button clicked
            idx_lead, (x0, x1, y0, y1) = self.ui.get_mru_caliper_coords()
            # ic(idx_lead, (x0, x1, y0, y1))
            x0 = self.rec.pd_time_to_count(x0)
            x1 = self.rec.pd_time_to_count(x1)
            cmt = [
                (x0 + x1) // 2,
                (y0 + y1) // 2,
                x0, y0,
                idx_lead, msg
            ]
            self.cmts.update_comment(cmt)
            cmt_saved = True

        idxs_lead = self.LD_TEMPL[template] if id_changed == ID_DPD_LD_TEMPL else self.idxs_lead
        self.ks_cmts, cmts = self.cmts.get_comment_list(idxs_lead)

        def _get_1st_line_idx(s):
            """ Index up until first new line char """
            idx = s.find('\n')
            return idx if idx != -1 else INF

        def _get_1st_words_idx(s, lim=self.MAX_PRV_LEN):
            """ Index up until the limit separated by space """
            st = s[:lim]
            if st.find(' ') != -1:
                return st.rindex(' ')
            else:
                return INF

        def _get_comment_preview(c):
            """ Split comment into short preview, returns None if the preview is the entire comment """
            if len(c) >= 30 or c.find('\n') != -1:  # Split into preview if it's a long comment or more than 1 line
                idx = min(_get_1st_line_idx(c), _get_1st_words_idx(c))
                if idx == INF:  # Degenerate case, not a word and no new line
                    idx = self.MAX_PRV_LEN
                return c[:idx]

        def _get_cmt_item(idx):  # This `idx` is unique
            x, idx_ld, c = cmts[idx]
            cp = _get_comment_preview(c)
            l = [
                dbc.Badge(id=m_id(ID_BDG_CMT_TM, idx), className=CNM_BDG_MY_INT, n_clicks=0,
                          children=self.rec.count_to_str(x)),
                dbc.Badge(className=CNM_BDG_MY, children=self.rec.lead_nms[idx_ld])
            ]
            # ic(cmts[idx], cp)
            if cp is not None:  # Should use preview
                l += [
                    html.P(className=CNM_CMT_TXT, children=cp),
                    html.Button(id=m_id(ID_BTN_CMT_ITM_TG, idx), className=CNM_BTN, n_clicks=0, children=[
                        html.I(id=ID_IC_CMT_ITM_TG, className=CNM_CMT_EXP)
                    ]),
                    dbc.Collapse(id=m_id(ID_CLP_CMT_ITM, idx), is_open=False, children=[
                        html.P(className=CNM_CMT_TXT, children=c)  # The entire comment
                    ]),
                ]
            else:  # Comment short enough
                l.append(html.P(className=CNM_CMT_TXT, children=c))
            return l

        # raise PreventUpdate  # The output really doesn't matter, just to trigger inner state change
        return cmt_saved, [dbc.ListGroupItem(className=CNM_CMT_BLK, action=True, children=_get_cmt_item(idx))
                           for idx in range(len(cmts))]

    def _get_all_annotations(self, idx_ann_clicked, idx_lead):
        """ Static tag and shape measurement annotations """
        anns = self.ui.get_caliper_annotations(idx_lead)
        if self.rec is not None and self._marking_on:
            anns += self.ui.get_tags(*(self.disp_rng[0]), idx_ann_clicked)
        return anns

    def update_lead_options_disable_layout_figures(
            self, record_name, template, layouts_fig, layout_tmb,
            n_clicks_adv_bk, n_clicks_mv_bk, n_clicks_fixy, n_clicks_mv_fw, n_clicks_adv_fw,
            n_clicks_mkg_tg, n_clicks_clpr,
            data_add, data_rmv,
            idx_ann_clicked, ns_clicks_cmt,
            plots, disables_lead_add, figs_gra: List[Dict[str, Dict]], fig_tmb, ns_clicks_tag):
        """Display lead figures based on current record and template selected, and based on lead selection in modal

        Initializes lead selections

        # Inputs
        :param record_name: Name of record selected on dropdown
        :param template: Name of template selected on dropdown

        :param layouts_fig: RelayoutData of actual plot
        :param layout_tmb: RelayoutData of global preview
        :param n_clicks_adv_bk: Number of clicks for advance back button
        :param n_clicks_mv_bk: Number of clicks for nudge back button
        :param n_clicks_fixy: Number of clicks for fix-yaxis button
        :param n_clicks_mv_fw: Number of clicks for nudge forward button
        :param n_clicks_adv_fw: Number of clicks for advance forward button
        :param n_clicks_mkg_tg: Number of clicks for toggle markings button
        :param n_clicks_clpr: Number of clicks for clear caliper measurements
        :param data_add: Tuple info on if adding took place and if so the lead index added
        :param data_rmv: Tuple info on the original index of removed lead index, and the lead index removed
        :param idx_ann_clicked: Index of tag clicked
        :param ns_clicks_cmt: Number of clicks for comment timestamp

        # States
        :param plots: Div list of of lead currently on plot
        :param disables_lead_add: List of disable boolean states for the add-lead items

        :param figs_gra: Graph object dictionary of actual plot
        :param fig_tmb: Graph object dictionary of global preview
        :param ns_clicks_tag: List on number of clicks for each tag

        .. note:: Previous record and figure overridden
        .. note:: Selections in modal are disabled if corresponding lead is shown
        """

        # Shared output must be in a single function call per Dash callback
        # => Forced to update in a single function call
        # ic()

        def _get_tag_annotations():
            """ Independent by lead """
            if self.rec is not None and self._marking_on:
                return self.ui.get_tags(*(self.disp_rng[0]), idx_ann_clicked)
            else:
                return []

        def _update_figs_annotations():
            tags = _get_tag_annotations()
            for i, f in enumerate(figs_gra):
                # ic(self.idxs_lead[i])
                f['layout']['annotations'] = tags + self.ui.get_caliper_annotations(self.idxs_lead[i])
                # ic(self.ui.get_caliper_annotations(self.idxs_lead[i]))

        def _update_lead_figures():
            # ic()
            strt, end = self.disp_rng[0]
            sample_factor = self.plt.get_sample_factor(strt, end)
            x_vals = self.rec.get_time_values(strt, end, sample_factor)
            lst_args = [(idx_idx, idx_lead, strt, end, sample_factor)  # The strt, end variables here cannot be saved
                    for idx_idx, idx_lead in enumerate(self.idxs_lead)]
            # ic(lst_args)
            # Multi-threading for mainly IO
            # for a in args:
            #     _set_y_vals(*a)
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.MAX_NUM_LD) as executor:
                # ic('inside threading')
                executor.map(lambda args: _set_y_vals(*args), lst_args)

            # ic()
            removed = self.ui.update_caliper_annotations_time(strt, end, figs_gra, self.idxs_lead)
            # ic()
            if removed:
                # self._shapes = figs_gra[0]['layout']['shapes']  # Pick any one, shapes already removed
                self.ui.highlight_mru_caliper_edit(figs_gra, self.idxs_lead)
            # anns = self._get_all_annotations(idx_ann_clicked)
            _update_figs_annotations()
            for f in figs_gra:  # Lines up with number of figures plotted
                # Short execution time, no need to multi-process
                f[D][0]['x'] = x_vals
                # f['layout']['annotations'] = anns
                # Without this line, the range displayed can be invalid
                f['layout']['xaxis']['range'] = x_layout_range  # This has to be the last assignment
            # ic()

        def _set_y_vals(idx_idx, idx_lead, strt, end, sample_factor):
            y_vals = self.rec.get_ecg_samples(idx_lead, strt, end, sample_factor)
            # ic(strt, end, y_vals)
            if self._yaxis_fixed:
                rang = figs_gra[idx_idx]['layout']['yaxis']['range']
                figs_gra[idx_idx][D][0]['y'] = y_vals
                figs_gra[idx_idx]['layout']['yaxis']['range'] = rang  # Preserves the original range, by intuition
            else:
                figs_gra[idx_idx][D][0]['y'] = y_vals
                figs_gra[idx_idx]['layout']['yaxis']['range'] = self.ui.get_ignore_noise_range(y_vals)
                # figs_gra[idx_idx]['layout']['yaxis']['range'] = self.ui.get_ignore_noise_range(strt, end)

        def _shift_is_out_of_lim(strt, end, offset):
            """ On advance and nudge navigation controls.

            Checks if doing a shift at edge that collapses start and end into the same time
            """
            # Guess no need to show an error alert, users will figure it out
            if offset < 0 and end + offset < 0:  # Shift back and end timestamp will be 0
                return True
            elif offset > 0 and strt + offset > self.rec.COUNT_END:
                return True
            else:
                return False

        def _create_comment_range_labels():
            c = self.ui.get_mru_caliper_coords()
            if c is not None:
                idx_lead, (x0, x1, y0, y1) = c
                (x0, x1, y0, y1) = (  # String representations
                    self.rec.pd_time_to_str(x0),
                    self.rec.pd_time_to_str(x1),
                    f'{int(y0):,}',
                    f'{int(y1):,}'
                )
                # idx_lead, coords = c
                # x0, x1, y0, y1 = coords
                return [
                    html.Div(id=ID_DIV_CMT_LB_LD, children=[
                        'On lead ',
                        dbc.Badge(className=CNM_BDG_MY, children=self.rec.lead_nms[idx_lead])
                    ]),
                    html.Div(id=ID_DIV_CMT_LB_T, children=[
                        'Time: ',
                        dbc.Badge(className=CNM_BDG_MY, children=x0),
                        '-',
                        dbc.Badge(className=CNM_BDG_MY, children=x1),
                    ]),
                    html.Div(id=ID_DIV_CMT_LB_V, children=[
                        'Voltage: ',
                        dbc.Badge(className=CNM_BDG_MY, children=y0),
                        '-',
                        dbc.Badge(className=CNM_BDG_MY, children=y1),
                        'mV'
                    ])
                ]
            else:
                return []
        # ic()
        changed_id_property = self.get_last_changed_id_property()
        changed_id = self.ui.get_id(changed_id_property)

        time_label = dash.no_update  # Both dependent on number of leads on plot == 0
        disable_export_btn = dash.no_update
        cmt_rng_label = dash.no_update
        disable_comment = dash.no_update
        if ID_STOR_REC == changed_id:  # Reset layout
            self.idxs_lead = []
            plots = []
            disables_lead_add = [False] * len(disables_lead_add)  # All options are not disabled
            if record_name is not None:
                fig_tmb = self.fig_tmb.add_trace([], override=True)  # Basically removes all trace without adding
                ns_clicks_tag = [0] * self.rec.N_TAG
            else:
                fig_tmb = dash.no_update
                ns_clicks_tag = []
            # lead_styles = [dash.no_update for i in range(len(self.idxs_lead))]
            time_label = None
            disable_export_btn = True
            figs_gra = [dash.no_update] * len(figs_gra)
        elif ID_DPD_LD_TEMPL == changed_id:
            if template is not None:
                self.idxs_lead = deepcopy(self.LD_TEMPL[template])  # Deepcopy cos idx_lead may mutate
                # Override for any template change could happen before
                # anns = self._get_all_annotations(idx_ann_clicked)
                self.ui.clear_measurements()  # Remove all caliper measurements as the easiest solution
                tags = _get_tag_annotations()
                plots = [self.get_fig_layout(idx, tags + self.ui.get_caliper_annotations(idx))
                         for idx in self.idxs_lead]
                # lead_styles = self.get_lead_height_styles()
                # Linear, more efficient than checking index in `self.idxs_lead`
                disables_lead_add = [False] * len(disables_lead_add)
                for idx in self.idxs_lead:
                    disables_lead_add[idx] = True
                fig_tmb = self.fig_tmb.add_trace(deepcopy(self.idxs_lead), override=True)
                time_label = self.ui.count_pr_to_time_label(*self.disp_rng[0])
                disable_export_btn = False
            else:  # Reset layout
                self.idxs_lead = []
                plots = []
                # lead_styles = [dash.no_update for i in range(len(self.idxs_lead))]
                disables_lead_add = [False] * len(disables_lead_add)  # All options are not disabled
                # figs_gra = []  # For same reason below, the remove button case
                fig_tmb = self.fig_tmb.add_trace([], override=True)  # Basically removes all trace without adding
                time_label = None
                disable_export_btn = True
            figs_gra = [dash.no_update] * len(figs_gra)
            ns_clicks_tag = dash.no_update

        elif ID_GRA == changed_id and self.idxs_lead:  # != []; RelayoutData changed, graph has pattern matched ID
            # When a record is selected, ID_GRA is in changed_id for unknown reason
            idx_changed = self.ui.get_pattern_match_index(changed_id_property)
            idx_idx_changed = self._get_fig_index_by_index(idx_changed)
            # ic(layouts_fig[idx_idx_changed], figs_gra[idx_idx_changed]['layout'])
            l = layouts_fig[idx_idx_changed]
            if layouts_fig is not None and self.ui.K_XS in l:  # Navigation
                # Execution won't go in if adding a new lead, cos layout doesn't contain KEY_X_S on create
                l_c = figs_gra[idx_idx_changed]['layout']
                self.disp_rng[0] = self.ui.get_x_display_range(l_c)
                yaxis_rng_ori = l_c['yaxis']['range']
                fig_tmb['layout']['xaxis']['range'] = x_layout_range = \
                    self.ui.get_x_layout_range(layouts_fig[idx_idx_changed])
                # ic('call update lead figures')
                _update_lead_figures()
                # ic(x_layout_range, self.disp_rng[0])
                l_c['yaxis']['range'] = yaxis_rng_ori
                plots = dash.no_update
                # lead_styles = [dash.no_update for i in range(len(self.idxs_lead))]
                disables_lead_add = self.no_update_add_opns
                time_label = self.ui.time_range_to_time_label(*x_layout_range)
                cmt_rng_label = _create_comment_range_labels()
                disable_comment = not self.ui.has_measurement()
                # export button must've been on already
                ns_clicks_tag = dash.no_update
            # Change in caliper/user-drawn shape
            elif layouts_fig is not None and self.ui.shape_updated(l):
                self.ui.update_caliper_annotations_shape(l, idx_changed)
                # anns = self._get_all_annotations(idx_ann_clicked)
                # tags = self._get_tag_annotations(idx_ann_clicked)
                _update_figs_annotations()
                # self._shapes = figs_gra[idx_idx_changed]['layout']['shapes']
                self.ui.highlight_mru_caliper_edit(figs_gra, self.idxs_lead)
                cmt_rng_label = _create_comment_range_labels()
                disable_comment = not self.ui.has_measurement()
                # for idx, f in enumerate(figs_gra):  # Override original values, for potential text annotation removal
                #     # f['layout']['annotations'] = tags + self.ui.get_caliper_annotations(self.idxs_lead[idx])
                #     if idx != idx_idx_changed:
                #         f['layout']['shapes'] = self._shapes
            else:
                raise PreventUpdate
        elif ID_TMB == changed_id:  # Changes in thumbnail figure have to be range change
            # Workaround: At first app start, ID_TMB is in changed_id for unknown reason
            # ic(fig_tmb['layout'])
            if self.rec is not None:
                self.disp_rng[0] = self.ui.get_x_display_range(fig_tmb['layout'])
                x_layout_range = fig_tmb['layout']['xaxis']['range']
                _update_lead_figures()
                fig_tmb = dash.no_update
                plots = dash.no_update
                # lead_styles = [dash.no_update for i in range(len(self.idxs_lead))]
                disables_lead_add = self.no_update_add_opns
                time_label = self.ui.time_range_to_time_label(*x_layout_range)
                cmt_rng_label = _create_comment_range_labels()
                disable_comment = not self.ui.has_measurement()
                ns_clicks_tag = dash.no_update
            else:
                raise PreventUpdate

        elif ID_BTN_FIXY == changed_id:
            self._yaxis_fixed = not self._yaxis_fixed
            for f in figs_gra:
                f['layout']['yaxis']['fixedrange'] = n_clicks_fixy % 2 == 1
                fig_tmb = dash.no_update
                plots = dash.no_update
                disables_lead_add = self.no_update_add_opns
            ns_clicks_tag = dash.no_update
        elif ID_IC_TG_TG == changed_id:
            if self.rec is not None:
                # anns = self._get_all_annotations(idx_ann_clicked)
                # tags = self._get_tag_annotations(idx_ann_clicked)
                # for f in figs_gra:
                #     f['layout']['annotations'] = tags + self.ui.get_caliper_annotations()
                _update_figs_annotations()
                plots = dash.no_update
                disables_lead_add = self.no_update_add_opns
                fig_tmb = dash.no_update
                ns_clicks_tag = dash.no_update
            else:
                raise PreventUpdate
        elif ID_BTN_CLP_CLR == changed_id:
            self.ui.clear_measurements()
            # self._shapes = []
            # anns = self._get_all_annotations(idx_ann_clicked)
            _update_figs_annotations()
            cmt_rng_label = _create_comment_range_labels()  # Basically set to none
            disable_comment = not self.ui.has_measurement()
            # for f in figs_gra:
            #     f['layout']['shapes'] = self._shapes
            #     # f['layout']['annotations'] = anns
            plots = dash.no_update
            disables_lead_add = self.no_update_add_opns
            fig_tmb = dash.no_update
            ns_clicks_tag = dash.no_update

        elif self.move_offset_counts is not None and changed_id in self.move_offset_counts:
            # The keys: [ID_BTN_ADV_BK, ID_BTN_MV_BK, ID_BTN_MV_FW, ID_BTN_ADV_FW] by construction
            offset_count = self.move_offset_counts[changed_id]
            strt, end = self.disp_rng[0]
            if not _shift_is_out_of_lim(strt, end, offset_count):
                strt += offset_count
                end += offset_count
                strt, end = self.rec.keep_range(strt), self.rec.keep_range(end)
                self.disp_rng[0] = [strt, end]
                x_layout_range = [
                    self.rec.count_to_pd_time(strt),
                    self.rec.count_to_pd_time(end)
                ]
                _update_lead_figures()
                fig_tmb['layout']['xaxis']['range'] = x_layout_range
                plots = dash.no_update
                # lead_styles = [dash.no_update for i in range(len(self.idxs_lead))]
                disables_lead_add = self.no_update_add_opns
                time_label = self.ui.time_range_to_time_label(*x_layout_range)
                cmt_rng_label = _create_comment_range_labels()
                disable_comment = not self.ui.has_measurement()
                ns_clicks_tag = dash.no_update
            else:
                raise PreventUpdate

        elif ID_STOR_ADD == changed_id:  # A new lead layout should be appended, due to click in modal
            added, idx_add = data_add
            # Need to check if clicking actually added a lead
            if added:  # Else error alert will raise
                anns = self._get_all_annotations(idx_ann_clicked, idx_add)
                plots.append(self.get_fig_layout(idx_add, anns))
                disables_lead_add[idx_add] = True
                fig_tmb = self.fig_tmb.add_trace([idx_add], override=False)
                figs_gra = [dash.no_update] * len(figs_gra)
                if len(self.idxs_lead) == 1:  # from 0 to 1 lead
                    time_label = self.ui.count_pr_to_time_label(*self.disp_rng[0])
                    disable_export_btn = False
                ns_clicks_tag = dash.no_update
            else:
                raise PreventUpdate
        elif ID_STOR_RMV == changed_id:
            idx_idx_rmv, idx_rmv = data_rmv  # There will always be something to remove
            self.fig_tmb.remove_trace(idx_idx_rmv, idx_rmv)
            # Clear all potential caliper measurements on this lead before removal, to update MRU
            idxs_lead = deepcopy(self.idxs_lead)
            idxs_lead.insert(idx_idx_rmv, idx_rmv)
            # Need to resort back to assuming figure not yet removed
            if self.ui.update_caliper_lead_removed(idx_rmv):
                self.ui.highlight_mru_caliper_edit(figs_gra, idxs_lead, idxs_ignore=[idx_rmv])
                cmt_rng_label = _create_comment_range_labels()
            del plots[idx_idx_rmv]
            disables_lead_add[idx_rmv] = False
            # figs_gra = [dash.no_update] * len(figs_gra)
            # Surprisingly when I have the line below, Dash gives weird exception, instead of not having this line
            # del figs_gra[idx_idx_changed]'
            if len(self.idxs_lead) == 0:  # from 1 to 0 lead
                time_label = None
                disable_export_btn = True
            ns_clicks_tag = dash.no_update
        elif ID_STOR_TG_IDX == changed_id and idx_ann_clicked != -1 and idx_ann_clicked != self.rec.N_TAG:
            ns_clicks_tag[idx_ann_clicked] += 1
            count = self.rec.ms_to_count(self.rec.tags[idx_ann_clicked][1])

            strt, end = self.disp_rng[0]
            if not (strt <= count <= end):  # Navigate to point of annotation
                mid_range = (end - strt) // 2  # Keep the same width in terms of time
                strt, end = self.rec.get_shifted_range(count, mid_range)
                self.disp_rng[0] = [strt, end]
                x_layout_range = [
                    self.rec.count_to_pd_time(strt),
                    self.rec.count_to_pd_time(end)
                ]
                _update_lead_figures()
                fig_tmb['layout']['xaxis']['range'] = x_layout_range
                time_label = self.ui.count_pr_to_time_label(*self.disp_rng[0])
            else:  # Annotation clicked on is within display range
                fig_tmb = dash.no_update
                n_update = [dash.no_update] * len(figs_gra)
                anns = figs_gra[0]['layout']['annotations']  # Get current annotations on display with arbitrary figure
                l = len(anns)
                if l == 0:
                    figs_gra = n_update
                else:
                    strt_idx = anns[0]['idx']
                    if strt_idx <= idx_ann_clicked <= strt_idx + l - 1:
                        idx = bisect_left(list(range(strt_idx, strt_idx + l)), idx_ann_clicked)
                        for f in figs_gra:
                            f['layout']['annotations'][idx]['bgcolor'] = ANTN_BG_CLR_CLK
                    else:
                        figs_gra = n_update
            plots = dash.no_update
            disables_lead_add = self.no_update_add_opns
        elif ID_BDG_CMT_TM == changed_id:
            idx_cmt_ch = self.ui.get_pattern_match_index(changed_id_property)
            k = self.ks_cmts[idx_cmt_ch]
            # TODO
            raise PreventUpdate
        else:
            raise PreventUpdate
        # ic()
        self.idx_ann_clicked = idx_ann_clicked
        return (
            plots, disables_lead_add, figs_gra, fig_tmb,
            time_label, cmt_rng_label,
            disable_comment, disable_comment, disable_export_btn,
            ns_clicks_tag
        )

    @staticmethod
    def toggle_modal(n_clicks_add_btn, n_clicks_close_btn, is_open):
        # EcgApp.__print_changed_property('toggle show modal')
        return not is_open

    def toggle_max_lead_error(self, data_add, template, is_open):
        # EcgApp.__print_changed_property('toggle show max lead error')
        if self.ui.get_id(self.get_last_changed_id_property()) == ID_DPD_LD_TEMPL:
            # Make sure no change happens when a template is selected
            return False
        else:
            added, idx_add = data_add
            if not added and len(self.idxs_lead) >= self.MAX_NUM_LD:
                return not is_open
            else:
                return is_open

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
        # if self._yaxis_fixed:  # Init with yaxis unlocked
        if n_clicks % 2 == 0:
            return CNM_IC_LKO
        else:
            return CNM_IC_LK

    def toggle_show_markings(self, n_clicks):
        self._marking_on = not self._marking_on
        if n_clicks % 2 == 1:
            return join(CNM_TG_TG, ANM_BTN_TG_TG_ROTE)
        else:
            return join(CNM_TG_TG, ANM_BTN_TG_TG_ROTS)

    def export_csv(self, n_clicks):
        strt, end = self.disp_rng[0]
        return self.exp.export(strt, end, self.idxs_lead)

    @staticmethod
    def toggle_tags_n_comments_panel(n_clicks):
        if n_clicks % 2 == 0:
            return ANM_DIV_CMT_TG_CLPW, join(CNM_BTN, ANM_BTN_TG_BDR_SH), CNM_TG_EXP, ANM_DIV_PLT_EXPW
        else:
            return ANM_DIV_CMT_TG_EXPW, join(CNM_BTN, ANM_BTN_TG_BDR_HD), CNM_TG_EXP, ANM_DIV_PLT_CLPW

    @staticmethod
    def __print_changed_property(func_nm):
        # Debugging only
        print(f'in [{func_nm:<25}] with changed property: [{EcgApp.get_last_changed_id_property():<25}]')

    @staticmethod
    def example():
        ecg_app = EcgApp(__name__)
        ecg_app.app.title = "Example run"
        return ecg_app
