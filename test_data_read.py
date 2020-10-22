# -*- coding: utf-8 -*-
# import base64
# import io
# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# import plotly.graph_objs as go
# import plotly.express as px
# import pandas as pd
import pathlib
import os
import h5py
import json
import numpy as np

# from dash.dependencies import Input, Output  # , State

# from scipy import stats


DATA_PATH = pathlib.Path("/Users/stefanh/Documents/UMich/Research/ECG-Signal-Viewer/data")

selected_record = "LOG_DHR50526570_09000e6f-001.h5"
selected_file = "00000003.log"

record = h5py.File(DATA_PATH.joinpath(selected_record), 'r')
header = json.loads(record[selected_file].attrs['metadata'])

attrs = record[selected_file].attrs
print(attrs)
# print(attrs["metadata"])

for i in attrs:
    print(i)

