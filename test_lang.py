import pandas as pd
import numpy as np
import bisect
from functools import reduce

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from ecg_record import EcgRecord
from ecg_app import *

# from memory_profiler import profile

# def time_str_to_sample_count(time, sample_rate):
#     timestamp = pd.Timestamp(time)
#     timedelta = timestamp - pd.Timestamp('1970-01-01')
#     us = timedelta // pd.Timedelta('1us')
#     print(us * 2, 10**6)
#     return us * sample_rate // (10 ** 6)


# @profile
# def main():
#     d = {0: 'a'}
#     d[2] = 'b'
#     print()


if __name__ == "__main__":
    # rng = pd.date_range(pd.Timestamp("2018-03-10 09:00"), periods=3, freq='s')
    # print(rng, type(rng))
    # rng2 = rng.strftime('%r:%f')
    # print(rng2)
    # rng3 = rng.strftime('%Y-%m-%d %H:%M:%S:%f')
    # print(rng3, type(rng[1]))
    #
    # linspace = np.linspace(0, 100, num=99)
    #
    # print(3632348 / 3600 / 2000)
    #
    # a = np.arange(6).reshape(2, 3) + 10
    # print(a)
    # print(np.argmax(a, axis=0))
    # print(np.argmax(a, axis=1))

    # print(10**6 / 2000)
    #
    # lst = [20, 40, 60, 80, 100]
    # lst_new = [0] + lst
    # # print(reduce(lambda l, v: l.append(l[-1] + v), [lst_new]))
    # print(lst_new[1:])
    #
    # print(bisect.bisect_left(lst, 30))
    # print(bisect.bisect_right(lst, 30))
    # print(bisect.bisect_right(lst, 20))
    # print(bisect.bisect_left(lst, 20))
    # print(bisect.bisect_left(lst, 10))
    #
    # time_range = [10, 20]
    # print(np.arange(time_range[0], time_range[1]+1))

    # print(np.arange(0, 1000 + 1))
    # print(np.linspace(0, 1000, num=1000 + 1))

    # print(time_str_to_sample_count('1970-01-01 00:00:13.1558', 2000))
    # print(time_str_to_sample_count('1970-01-01 00:01:13.1558', 2000))

    # main()

    # strt = 0
    # end = 100000
    # a = np.arange(end + 1)
    # step = (end - strt + 1) // 4435
    # print(step)
    # print(a[::step].shape)
    #
    # d = {'margin': {'l': 0, 'r': 0, 't': 0, 'b': 200}, 'xaxis': {
    #     'rangeslider': {'visible': True, 'bgcolor': 'rgba(229, 236, 246, 0.8)', 'thickness': 1,
    #                     'yaxis': {'_template': None, 'rangemode': 'match'}, 'autorange': True,
    #                     'range': ['1970-01-01', '1970-01-01 03:51:03.907']}, 'type': 'date',
    #     'range': ['1970-01-01 01:58:24.8202', '1970-01-01 02:43:04.2536'], 'autorange': False}}

    # d = [24386254, 27727814]
    # d = [24633501, 27727814]
    # s = 6876
    # rec = EcgRecord.example()
    # print((d[1] - d[0]) / 10306)
    # a = rec.get_samples(3, d[0], d[1], s)
    # print(a, a.shape)

    # print(dbc.themes.LUX)

    app = dash.Dash()
    app.layout = html.Div(className=CNM_HD, children=[
        html.Button(id=ID_BTN_OPN, className=CNM_BTN, n_clicks=0, children=[
            'sdad'
        ]),
        html.H1(TXT_HD, className=CNM_HDTT)
    ])
    app.run_server(debug=True)
