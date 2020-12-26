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

    ecg_app.run(True)


if __name__ == "__main__":
    main()

