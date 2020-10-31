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
# import os
import h5py
import json
# import numpy as np

# from dash.dependencies import Input, Output  # , State

# from scipy import stats

from ecg_record import *

# enum SignalType { UNUSED = 0, ECG = 1, BOX = 2, PRESSURE = 3, ANALOG = 4, STIM = 5 };

DATA_PATH = pathlib.Path("/Users/stefanh/Documents/UMich/Research/ECG-Signal-Viewer/data")

selected_record = "LOG_DHR50526570_09000e6f-001.h5"

if __name__ == "__main__":
    record = h5py.File(DATA_PATH.joinpath(selected_record), 'r')
    files = list(record.keys())  # contains only log files
    print("Keys for a `record`: ")
    print(files)
    print()

    selected_file = files[3]
    print(type(record[selected_file]))
    attrs = record[selected_file].attrs  # attributes of the log
    # print(attrs)
    # # print(attrs["metadata"])
    # for i in attrs:
    #     print(i)
    print("metadata for each `file` of a `record`: ")
    print(list(attrs))  # contains only metadata
    print()

    header = json.loads(record[selected_file].attrs['metadata'])
    globalHeader = header.copy()
    globalHeader['sigheader'] = []  # cos it's a long list of dictionaries
    print("global/shared metadata for all `sigheader`s of a `file`: ")
    print(globalHeader)
    print()
    print('metadata for a few `sigheader`s: ')
    for i in range(5):
        print(header['sigheader'][i])
    # print("Signal 0 has this data: " + str(header['sigheader'][0]))
    print()

    print("metadata for a `record`: ")
    print(list(record.attrs))  # attributes of the entire surgery
    annotations = json.loads(record.attrs['annotations'])
    print("header for the list of `annotation`: ")
    print(annotations[0])
    print()
    print("the 2nd element in the list of `annotations` is protocol: ")
    print(annotations[1])
    print()

    num = 10
    print(f"the first {num}/{len(annotations)} elements of a `record`'s `annotation`: ")
    for i in range(2, num+1):
        print(annotations[i])
    print()

    print("several global metadata for each log file: ")
    my_record = EcgRecord(DATA_PATH.joinpath(selected_record))
    print(len(my_record.get_segment_keys()))
    for key in my_record.get_segment_keys():
        print(my_record.get_segment(key).get_metadata())
