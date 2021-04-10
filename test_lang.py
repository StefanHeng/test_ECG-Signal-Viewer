import pandas as pd
import numpy as np
from bisect import bisect_left, bisect_right
from functools import reduce
import re
import json

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from data_link import *
from dev_helper import *
from ecg_record import EcgRecord
from ecg_plot import EcgPlot
from ecg_ui import EcgUi
from ecg_app import EcgApp

from icecream import ic
# from memory_profiler import profile

# def time_str_to_sample_count(time, sample_rate):
#     timestamp = pd.Timestamp(time)
#     timedelta = timestamp - pd.Timestamp('1970-01-01')
#     us = timedelta // pd.Timedelta('1us')
#     print(us * 2, 10**6)
#     return us * sample_rate // (10 ** 6)


from enum import Enum  # for enum34, or the stdlib version
# from aenum import Enum  # for the aenum version

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

    # d = [24633501, 27727814]
    # s = 6876
    # rec = EcgRecord.example()
    # print((d[1] - d[0]) / s)
    # a = rec.get_samples(3, d[0], d[1], s)
    # print(a, a.shape)

    # print(dbc.themes.LUX)

    # s = "{\"index\":1,\"type\":\"graph\"}.relayoutData"
    # print(s)
    # m = re.match("^{\"index\":([0-9]+)", s)
    # print(m.group(1))  # Returns the first parenthesised subgroup

    # print(pd.Timestamp('1970-01-01'))
    # print(str(pd.Timestamp('1970-01-01')))

    # app = EcgApp.example()
    # app.curr_rec = EcgRecord(DATA_PATH.joinpath(record_nm))
    # app.curr_plot = EcgPlot(app.curr_rec, app)  # A `plot` serves a record
    # fig = app.curr_plot.get_thumb_fig_skeleton([6, 5, 3, 16, 35])
    # fig.show()
    #
    # rec = EcgRecord.example()
    # # strt, end = 10867132, 13896086
    # # ic(rec.COUNT_END)
    # # ic(rec._ann_tm[-1])
    # # # ic(strt, end, rec.get_annotation_indices(strt, end))
    # # strt_ms, end_ms = 6496922, 6722482
    # # ic(bisect_left(rec._ann_tm, strt_ms))
    #
    # idx = 8119934
    # print(np.argmax(rec.get_ecg_samples(29, 0, rec.COUNT_END)))

    # a = np.array([1 + 2j, 3 + 4j, 5 + 6j])
    # ic(np.abs(a))
    # a = np.arange(5)
    # ic(a[1:2])

    # p = DATA_PATH.joinpath(record_nm)
    # ic(p, str(p))
    # ic(p.stem)

    # k = 'shapes[22].x0'
    # n = 'sajd'
    # m = re.match(r'^shapes\[([0-9]+)]\.(.){2}$', k)
    # m2 = re.match(r'^shapes\[([0-9]+)]\.(.){2}$', n)
    # ic(m, int(m.group(1)))
    # ic(m2)

    # t1 = '1970-01-01 00:00:36.481'
    # t2 = '1970-01-01 00:00:41.3325'
    # t_max = pd.to_timedelta(10, unit='s')
    # t1_p = pd.to_datetime(t1)
    # t2_p = pd.to_datetime(t2)
    # d = (t2_p - t1_p) / 2
    # ic(d, type(d.microseconds // 1000))
    # ic(t1_p + d)
    # ic(d < t_max)

    # l = [
    #     [1, 2, 3],
    #     [4, 5, 6]
    # ]
    # ic([i for s in l for i in s])
    # ic(np.concatenate(l))

    # d = {
    #     1: 'a',
    #     2: 'b'
    # }
    # v = d.values()
    # ic(v, type(v), list(v))

    # d = {'shapes': [{'editable': True,
    #                                  'fillcolor': 'rgba(252, 169, 18, 0.1)',
    #                                  'fillrule': 'evenodd',
    #                                  'layer': 'above',
    #                                  'line': {'color': 'rgba(252, 169, 18, 0.7)',
    #                                           'dash': 'solid',
    #                                           'width': 2},
    #                                  'opacity': 1,
    #                                  'type': 'rect',
    #                                  'x0': '1970-01-01 00:00:30.6257',
    #                                  'x1': '1970-01-01 00:00:37.9448',
    #                                  'xref': 'x',
    #                                  'y0': 11144.260662336996,
    #                                  'y1': -13892.731818866012,
    #                                  'yref': 'y'}]}
    # ic('shapes' in d)

    # lst = [1, 2, 3]
    # for idx, i in enumerate(lst[::-1]):
    #     ic(idx, i)

    # a = 123_456_213_23
    # ic("{:,}".format(a))
    # ic(f'{a:,}')

    # rec = EcgRecord.example()
    # v = rec.get_time_values(0, 1000)
    # ic(v[0], v.iat[-1])
    # Animal = Enum('Animal', 'ant bee cat dog')
    #
    # ic(Animal.ant)  # returns <Animal.ant: 1>
    # ic(Animal['ant'])  # returns <Animal.ant: 1> (string lookup)
    # ic(Animal.ant.name)  # returns 'ant' (inverse lookup)
    # ic(Animal(1).name)

    # ic(np.random.choice(10, size=19, replace=False))
    # ic(np.percentile(np.arange(20), 85))

    # cmt1 = [20, 30, 12, 3, 'haha']
    # cmt2 = [20, 30, 12, 3, 'he']
    # ic(cmt1 < cmt2)
    #
    # cmt0 = [0, 0, 0, 0, 0, 'as']
    # cmt3 = [40, 0, 0, 0, 0, 'asd']
    # cmts = [cmt0, cmt1, cmt2, cmt3]
    # cmt_s = [60, 30, 12, 3, 'a']
    # ic(bisect_left(cmts, cmt1), bisect_right(cmts, cmt1))
    # ic(bisect_left(cmts, cmt_s), bisect_right(cmts, cmt_s))
    #
    # cmts.insert(4, cmt_s)
    # ic(cmts)
    # cfg = 'config.json'
    # with open(cfg, 'w') as f:
    #     json.dump(cmts, f)

    # cs = json.load(open(cfg, 'r'))
    # ic(cs)

    # st2 = 'blah\nhaha'
    # ic(st2.partition('\n'))
    # ic(st2[:st2.find('\n')])
    # st = 'Split the string at the first occurrence of *sep*, and return a 3-tuple containing the part ' \
    #     'before the separator, the separator itself, '
    #
    #
    # def _get_words_by_lim(c, lim=30):
    #     # s = ''
    #     # l = 0
    #     # wd, c = c.partition(' ')
    #     # l_wd = len(wd)
    #     # while l + l_wd <= lim:
    #     #     s += wd
    #     #     l += l_wd
    #     #     wd, c = c.partition(' ')
    #     #     l_wd = len(wd)
    #     # return s
    #     s = c[:lim]
    #     s = s[:s.rindex(' ')]
    #     return s
    #
    # ic(_get_words_by_lim(st))

    # s = 'asd'
    # ic(s.find(' '))
    inf = float('inf')
    ic(float('inf') == inf)


