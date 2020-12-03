# import pandas as pd
# import numpy as np
# import bisect
# from functools import reduce
from memory_profiler import profile

# def time_str_to_sample_count(time, sample_rate):
#     timestamp = pd.Timestamp(time)
#     timedelta = timestamp - pd.Timestamp('1970-01-01')
#     us = timedelta // pd.Timedelta('1us')
#     print(us * 2, 10**6)
#     return us * sample_rate // (10 ** 6)


@profile
def main():
    d = {0: 'a'}
    d[2] = 'b'
    print()


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

    main()
