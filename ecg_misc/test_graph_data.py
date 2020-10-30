# -*- coding: utf-8 -*-
# import base64
# import io
# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# import plotly.graph_objs as go
# import plotly.express as px
# import pandas as pd
# import os
import h5py
# import numpy as np

# from dash.dependencies import Input, Output  # , State

# from scipy import stats

from ecg_misc.test_data_read import DATA_PATH, selected_record

if __name__ == "__main__":
    record = h5py.File(DATA_PATH.joinpath(selected_record), 'r')
    files = list(record.keys())  # contains only log files
    print(files)
    print()

    selected_file = files[0]  # This is the file name, as dict key, not the file itself
    dataset = record[selected_file]
    print(type(dataset), dataset.dtype, dataset.shape)
    # print(dataset.shape[0] * dataset.shape[1], dataset.size)
    print()

    lead = dataset[0]
    print(type(lead), lead.dtype, lead.shape)

    # print(lead[100:500])
    # plt.plot(lead[:3000])
    # plt.xlabel('sample #')
    # plt.ylabel('mV')
    # plt.title('lead signal')
    # plt.show()

    # print(dataset['I'])




