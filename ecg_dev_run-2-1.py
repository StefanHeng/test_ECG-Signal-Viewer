import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH

# from memory_profiler import profile

from ecg_app import *


# @profile
def main():
    ecg_app = EcgApp(__name__)
    ecg_app.app.title = "Dev test run"

    # def update_lims_thumb(relayout_data, d_range):
    #     print(relayout_data)
    #     return d_range
    #
    # ecg_app.app.callback(
    #     Output(mch(ID_STOR_D_RNG), D),
    #     [],
    #     [State(mch(ID_STOR_D_RNG), D)],
    #     prevent_initial_call=True
    # )(update_lims_thumb)

    ecg_app.run(True)


if __name__ == "__main__":
    main()
