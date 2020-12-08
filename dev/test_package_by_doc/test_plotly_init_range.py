import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH

from dev_helper import *
from ecg_app import *


def main():
    ecg_app = EcgApp(__name__)
    ecg_app.curr_recr = EcgRecord(DATA_PATH.joinpath(record_nm))
    ecg_app.curr_plot = EcgPlot(ecg_app.curr_recr, ecg_app)  # A `plot` servers a record
    ecg_app.app.layout = html.Div(className=CNM_DIV_TMB, children=[
        dcc.Graph(
            id=ID_TMB, className=CNM_TMB,
            figure=ecg_app.get_thumb_fig(3)
        )
    ])

    ecg_app.run(True)


if __name__ == "__main__":
    main()
