import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL

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
ID_STOR_D_RNG = 'store_display_range'  # Contains dictionary of each display range

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
ID_MD_LD_ITM = 'modal_lead-selection-item'
ID_STOR_IDX_ADD = 'store_lead-idx-add'  # Current index of lead to add to layout
ID_RDO_LD_ADD = 'radio-group_lead-add'

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
        DEV_TML_RG: list(range(8)),
        DEV_TML_RD: [6, 4, 5, 3, 9, 16, 35, 20]
    }

    def __init__(self, app_name):
        self.curr_rec = None  # Current record
        self.curr_plot = None
        self.idxs_fig = []

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
                ]),

                dcc.Store(id=ID_STOR_IDX_ADD),
                html.Div(id=ID_DIV_ADD, children=[
                    dbc.Modal(id=ID_MD_ADD, centered=True, is_open=False, scrollable=True, children=[
                        dbc.ModalHeader(id=ID_MDHD_ADD, children=[
                            html.H5(TXT_ADD_LD, className=CNM_ADD_LD),
                            html.Button(id=ID_BTN_MD_CLS, className=CNM_BTN, n_clicks=0, children=[
                                html.I(className=CNM_IC_MD_CLS)
                            ])
                        ]),
                        dbc.ModalBody(id=ID_MDBD_ADD, children=[
                            # html.Div(id=ID_DIV_MD_ADD, className=CNM_BTS_LST)
                            # Design hack, list group items handled internally by radio button group
                            dcc.RadioItems(id=ID_RDO_LD_ADD, className=CNM_BTS_LST, labelClassName=CNM_BTS_LST_ITM)
                        ])
                    ])
                ])
            ])
        ])

    def get_fig_layout(self, idx):
        return html.Div(
            className=CNM_DIV_LD, children=[
                # All figure data maintained inside layout variable
                dcc.Store(id=m_id(ID_STOR_D_RNG, idx), data=self.curr_plot.D_RNG_INIT),

                html.Div(className=CNM_DIV_LDNM, children=[
                    html.P(self.curr_rec.lead_nms[idx], className=CNM_LD)
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
                            html.Button(id=m_id(ID_BTN_FIXY, idx), className=join(CNM_BTN, CNM_BTN_FIG_OPN),
                                        n_clicks=0, children=[
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
        )(self.toggle_div_options)

        # self.app.callback(
        #     Output(ID_STOR_IDX_ADD, D),
        #     Input(mch(ID_MD_LD_ITM), NC),
        #     State(mch(ID_MD_LD_ITM), 'id')
        # )(self.set_last_add_idx)

        self.app.callback(
            [Output(ID_DPD_LD_TEMPL, 'disabled'),
             Output(ID_BTN_ADD, 'disabled')],
            Input(ID_DPD_RECR, V)
        )(self.toggle_disable)

        self.app.callback(
            Output(ID_RDO_LD_ADD, 'options'),
            [Input(ID_DPD_RECR, V),
             Input(ID_DPD_LD_TEMPL, V),
             Input(ID_RDO_LD_ADD, V)],
            [State(ID_RDO_LD_ADD, 'options')]
        )(self.update_template_dropdown_and_add_options)

        self.app.callback(
            Output(ID_DIV_PLTS, C),
            [Input(ID_DPD_LD_TEMPL, V),
             Input(ID_RDO_LD_ADD, V)],
            State(ID_DIV_PLTS, C)
        )(self.update_lead_layout)

        # self.app.callback(
        #     [Output(ID_DIV_PLTS, C),
        #      Output(ID_DIV_ADD, CNM),
        #      Output(all_(ID_MD_LD_ITM), CNM)],
        #     [Input(ID_DPD_LD_TEMPL, V),
        #      Input(mch(ID_MD_LD_ITM), NC)],
        #     [State(mch(ID_MD_LD_ITM), 'id'),
        #      State(ID_DIV_PLTS, C),
        #      State(ID_DIV_ADD, CNM),
        #      State(all_(ID_MD_LD_ITM), CNM)]
        # )(self.update_leads)

        self.app.callback(
            Output(ID_MD_ADD, 'is_open'),
            [Input(ID_BTN_ADD, NC),
             Input(ID_BTN_MD_CLS, NC),
             Input(ID_RDO_LD_ADD, V)],
            [State(ID_MD_ADD, 'is_open')],
            prevent_initial_call=True
        )(self.toggle_modal)

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

    def update_template_dropdown_and_add_options(self, rec_nm, template, idx_lead, lead_options):
        """Display lead figures based on current record and template selected, and based on lead selection in modal

        Initializes lead selections

        :param rec_nm: Name of record selected on dropdown
        :param template: Name of template selected on dropdown
        :param idx_lead: Index of changed lead
        :param lead_options: Layout on all selections

        .. note:: Previous record and figure overridden
        .. note:: Selections in modal are disabled if corresponding lead is shown
        """
        # Shared output must be in a single function call per Dash callback

        changed_id = self.get_last_changed_id()
        if ID_DPD_RECR in changed_id:
            if rec_nm is not None:
                self.curr_rec = EcgRecord(DATA_PATH.joinpath(rec_nm))
                self.curr_plot = EcgPlot(self.curr_rec, self)  # A `plot` serves a record
                # Must generate selections now, for users could not select a template, and customize lead by single add
                return [{L: f'{idx+1}: {nm}', V: idx} for idx, nm in enumerate(self.curr_rec.lead_nms)]
            else:
                return lead_options  # Keep unchanged
        elif ID_DPD_LD_TEMPL in changed_id:
            if template is not None:
                self.idxs_fig = self.LD_TEMPL[template]
                # Template dropdown is of course not disabled
                return [
                    {L: f'{idx + 1}: {nm}', V: idx, 'disabled': idx in self.idxs_fig}
                    for idx, nm in enumerate(self.curr_rec.lead_nms)
                ]
            else:
                return lead_options
        elif ID_RDO_LD_ADD in changed_id:  # A new lead layout should be appended, due to click in modal
            self.idxs_fig.append(idx_lead)
            lead_options[idx_lead]['disabled'] = True
            # Hides the modal on first and any single click
            return lead_options
        else:
            return lead_options

    def update_lead_layout(self, template, idx_lead, plots):
        changed_id = self.get_last_changed_id()
        if ID_DPD_LD_TEMPL in changed_id:
            if template is not None:
                self.idxs_fig = self.LD_TEMPL[template]
                return [self.get_fig_layout(idx) for idx in self.idxs_fig]
            else:
                self.idxs_fig = None
                return None
        elif ID_RDO_LD_ADD in changed_id:
            plots.append(self.get_fig_layout(idx_lead))
            return plots
        else:
            return plots

    def update_leads(self, key_templ, n_clicks, id_d, plots, class_name_add, item_class_names):
        """Set up multiple lead/channel, original figures shown overridden,
         or append corresponding lead/channel by modal lead selection

        :param key_templ: Value of dropdown on template selected
        :param n_clicks: #clicks for the clicked lead option
        :param id_d: Pattern-matching id for the clicked lead option
        :param plots: Current app layout
        :param class_name_add: class of the add button div, used for opacity change
        :param item_class_names: list of class of lead options in add modal
        """
        changed_id = self.get_last_changed_id()
        if ID_MD_LD_ITM in changed_id:
            idx = id_d[I]
            self.idxs_fig.append(idx)
            # Hides the modal on first and any single click
            return plots, class_name_add, join(ID_MD_LD_ITM, 'disabled'), plots.append(self.get_fig_layout(idx))
        else:
            if key_templ is not None:
                self.idxs_fig = self.LD_TEMPL[key_templ]
                return [self.get_fig_layout(idx) for idx in self.idxs_fig], ANM_OPQY, [
                    join(ID_MD_LD_ITM, 'disabled' if idx in self.idxs_fig else '') for idx in self.idxs_fig
                ], item_class_names
            else:
                return [], ANM_OPQN, item_class_names

    @staticmethod
    def toggle_modal(n_clicks_add, n_clicks_close, idx_lead, is_open):
        return not is_open

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

