from dash.dependencies import MATCH, ALL

import plotly.graph_objects as go


FA_CSS_LNK = 'https://use.fontawesome.com/releases/v5.8.1/css/all.css'

CNM_HD = 'header'
ID_HDTT = 'header_title'
TXT_HD = 'Ecg Viz'  # Text shown in header
# ID_FD_TMB = 'fade_graph-thumbnail'
ID_FD_MN = 'fade_body-main'
CNM_MNBD = 'body_main'
# ID_STOR_IDXS_LD = 'store_idxs_lead'

ID_BBX_DIV_OPN = 'div_options-bound-box'
ID_DIV_OPN = 'div_options'
CNM_IC_BR = 'fas fa-bars'
ID_BTN_OPN = 'btn_options'
ID_IC_OPN = 'ic_options'

ID_DPD_RECR = 'record-dropdown'
ID_DPD_LD_TEMPL = 'lead-template-dropdown'
ID_STOR_REC = 'store_record-change'
# ID_STOR_TPL = 'store_template-change'

ID_DIV_TABS = 'div_tabs'  # Parent of lead channel plots and the annotation panel
ID_DIV_PLTS = 'div_plots'
ID_DIV_LD = 'div_lead'
CNM_DIV_LD = 'div_lead'
CNM_DIV_FD = 'div_lead-fade'  # For the fade animation

CNM_DIV_LDNM = 'div_lead-name'
CNM_LD = 'lead-name'
CNM_DIV_TMB = 'div_graph-thumbnail'
CNM_DIV_FIG = 'div_graph'
CNM_TMB = 'channel-graph-thumbnail'
CNM_GRA = 'channel-graph'
ID_TMB = 'figure-thumbnail'
ID_GRA = 'graph'
# ID_STOR_D_RNG = 'store_display_range'  # Contains dictionary of each display range
# ID_INTVL = 'interval'
ID_BTN_LD_RMV = 'btn_lead-remove'
CNM_IC_RMV = 'fas fa-minus'
ID_BTN_LD_RMV_WP = 'btn-wrapper_lead-remove'
TTP_PLCM = 'right'  # ToolTip placement
TTP_PLCM_PLT_CTRL = 'bottom'
TTP_OFST = 0
TTP_DL = 200  # ToolTIp delay

# ID_DIV_ADD = 'div_add'
ID_BTN_ADD = 'btn_add'
ID_IC_ADD = 'ic_add'
CNM_IC_ADD = 'fas fa-plus'

ID_BTN_EXP = 'btn_csv-export'
CNM_IC_EXP = 'fas fa-file-export'
ID_DLD_CSV = 'download_csv'

ID_MD_ADD = 'modal_add'
ID_MDHD_ADD = 'modal-header_add'
# CNM_MDTT = 'modal_title'
CNM_ADD_LD = 'title_add-lead'
TXT_ADD_LD = 'Add a lead/channel: '
ID_BTN_MD_CLS = 'btn_modal-close'
CNM_IC_MD_CLS = 'fas fa-times'
ID_MDBD_ADD = 'modal-body_add'
# ID_DIV_MD_ADD = 'div_modal-add'

# CNM_BTS_LST = 'list-group'  # For Bootstrap CSS
# CNM_BTS_LST_ITM = 'list-group-item list-group-item-action'
# ID_STOR_IDX_ADD = 'store_lead-idx-add'  # Current index of lead to add to layout
# ID_RDO_LD_ADD = 'radio-group_lead-add'
# CNM_RDO_ITM_IPT = 'input_null'
ID_GRP_LD_ADD = 'list-group_lead-add'
ID_ITM_LD_ADD = 'list-item_lead-add'

ID_ALT_MAX_LD = 'alert_max-lead-error'

ID_STOR_ADD = 'store_lead-add-change'
ID_STOR_RMV = 'store_lead-rmv-change'
ID_STOR_N_LD = 'store_num-lead'

ID_DIV_PLT_CTRL = 'div_plot-controls'
ID_BTN_ADV_BK = 'btn_advance-back'
ID_BTN_MV_BK = 'btn_move-back'  # Smaller in magnitude
ID_BTN_ADV_FW = 'btn_advance-forward'
ID_BTN_MV_FW = 'btn_move-forward'  # Smaller in magnitude
CNM_ADV_BK = 'fas fa-angle-double-left'
CNM_MV_BK = 'fas fa-angle-left'
CNM_ADV_FW = 'fas fa-angle-double-right'
CNM_MV_FW = 'fas fa-angle-right'
ID_BTN_TG_TG = 'btn_tag-toggle'
ID_IC_TG_TG = 'ic_tag-toggle'
CNM_TG_TG = 'fas fa-marker'

ID_DIV_TMLB = 'div_time-label'
ID_TMLB = 'time-label'

ID_DIV_TG = 'div_tags'
ID_GRP_TG = 'list-group_tags'
ID_IC_TG = 'ic_tag'
CNM_TG_EXP = 'fas fa-chevron-left'  # Expand
CNM_TG_CLP = 'fas fa-chevron-right'  # Collapse
ID_ITM_TG = 'item_tag'
ID_STOR_TG_IDX = 'store_clicked-tag-index'  # semi-store in a sense
ID_STOR_TG_NCS = 'store_tag-ns-clicks'
ID_STOR_REC_TGS = 'store_rec-tags'
CNM_TG_TXT = 'text_tag'
CNM_TG_BLK = 'tag-block'

ID_BTN_CMT_TG_TG = 'btn_comments-n-tags-toggle'  # Collapse or expand comments & tags panel

ID_DIV_CMT_TG = 'div_comments-n-tags'  # The 2nd tab
ID_DIV_CMT_ED = 'div_comment-edit'
ID_DIV_CMT_LST = 'div_comment-list'
ID_TXTA_CMT = 'text-area_comment'
ID_BTN_CMT_SBM = 'btn_comment-submit'

ID_DIV_CMT_LB = 'div_comment-label'
ID_DIV_CMT_LB_LD = 'div_comment-label-lead'
ID_DIV_CMT_LB_T = 'div_comment-label-time'
ID_DIV_CMT_LB_V = 'div_comment-label-volt'


CNM_BDG = 'bdg'
CNM_BDG_LT = 'badge-light'
CMN_TMLB = 'time-label'

ID_BTN_CLP_CLR = 'btn_clear-caliper'
CNM_CLP_CLR = 'fas fa-broom'

ANM_OPQY = 'opaque_1'  # Transition achieved by changing class
ANM_OPQN = 'opaque_0'
ANM_DIV_OPN_EXPW = 'div_options_expand-width'
ANM_DIV_OPN_CLPW = 'div_options_collapse-width'
ANM_DIV_PLT_CLPW = 'div_plots_expand-width'
ANM_DIV_PLT_EXPW = 'div_plots_collapse-width'
ANM_IC_OPN_ROTS = 'ic_options_rotate_start'
ANM_IC_OPN_ROTE = 'ic_options_rotate_end'
ANM_DIV_CMT_TG_EXPW = 'div_comments-n-tags_expand-width'
ANM_DIV_CMT_TG_CLPW = 'div_comments-n-tags_collapse-width'
ANM_BTN_TG_BDR_SH = 'btn_tag_show-left-border'
ANM_BTN_TG_BDR_HD = 'btn_tag_hide-left-border'
ANM_BTN_TG_TG_ROTS = 'ic-btn-tags-toggle_rotate-start'
ANM_BTN_TG_TG_ROTE = 'ic-btn-tags-toggle_rotate-end'

CNM_BTN = 'btn'  # To override LUX bootstrap theme
CNM_MY_DPD = 'my_dropdown'
ID_DIV_FIG_OPN = 'div_fig-options'
CNM_BTN_FIG_OPN = 'btn_fig-options'
ID_BTN_FIXY = 'btn_fix_yaxis'
ID_IC_FIXY = 'ic_fix_yaxis'
CNM_IC_LK = 'fas fa-lock'  # Font Awesome
CNM_IC_LKO = 'fas fa-lock-open'
# ID_STOR_IS_FIXY = 'id_is_yaxis_fixed'

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
DS = 'disabled'


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


def lst_to_tuple(lst):
    return *lst,


DEV_TML_S = 'single -> 1: I'
DEV_TML_RG = 'range(8) -> [1, 8]'
DEV_TML_RD = 'rand -> [7, 6, 4, 17, 36]'


# Styles
ANTN_BG_CLR = 'rgba(192, 192, 192, 0.3)'  # As in plotly annotations
ANTN_BG_CLR_A5 = 'rgba(192, 192, 192, 0.5)'
ANTN_BG_CLR_CLK = 'rgba(252, 169, 18, 0.3)'  # primary a3
ANTN_CLR = 'rgba(0, 0, 0, 0.6)'
ANTN_ARW_CLR = 'rgba(0, 0, 0, 0.7)'
LUX_FT_FML = '"Nunito Sans", ' \
             '-apple-system, ' \
             'BlinkMacSystemFont, ' \
             '"Segoe UI", ' \
             'Roboto, ' \
             '"Helvetica Neue", ' \
             'Arial, ' \
             'sans-serif, ' \
             '"Apple Color Emoji", ' \
             '"Segoe UI Emoji", ' \
             '"Segoe UI Symbol'

CLR_PLT_DF = '#6AA2F9'  # Default blue by plotly
CLR_PLT = '#2C2925'
PRIMARY = '#FCA912'
SECONDARY = '#2C8595'
SECONDARY_2 = '#80B6BF'
GRAY_0 = '#808080'  # Gray
DEFAULT_BG = 'rgba(229, 236, 246, 0.8)'
CLR_FONT = 'rgb(102, 102, 102)'  # Color of font
TRANSP = 'rgba(0, 0, 0, 0)'

# CLR_CLPR_A7 = 'rgba(252, 169, 18, 0.7)'
CLR_CLPR_RECT = 'rgba(253, 203, 113, 0.51)'
CLR_CLPR_RECT_ACT = 'rgba(252, 169, 18, 0.51)'  # Color for the most recent edited caliper measurement
# CLR_CLPR_A1 = 'rgba(252, 169, 18, 0.1)'


CONF = dict(  # Configuration for figure
    responsive=True,
    scrollZoom=True,
    modeBarButtonsToRemove=['lasso2d', 'autoScale2d', 'toggleSpikelines',
                            'hoverClosestCartesian', 'hoverCompareCartesian'],
    modeBarButtonsToAdd=[
        # 'select2d',
        'drawrect', 'eraseshape'
    ],
    displaylogo=False
)

TPL_SHAPE = dict(
    editable=True,
    fillcolor=CLR_CLPR_RECT,
    line=dict(
        color=TRANSP,
        width=2,
    ),
    xref='x',
    yref='y'
)

TPL = go.layout.Template()
TPL.layout.annotationdefaults = dict(
    font=dict(
        family=LUX_FT_FML,
        size=10.5,
        color=ANTN_CLR
    ),
    showarrow=False,
    opacity=1,
    align='center',
    xref="x",
    yref='y',
)
