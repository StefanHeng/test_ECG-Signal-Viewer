import numpy as np
import pandas as pd
import pyarrow as pa
import timeit
from datetime import timedelta
import sys

size = 3632348
ms_rand = 1497625.5  # A typical float passed into time conversion
sample_rate = 2000


def convert_readable(time_ms):
    time_s = time_ms / 1000
    return time_s // 3600, time_s // 60, time_s % 60, time_ms % 1000


def convert_readable_str(time_ms):
    time_s = time_ms / 1000
    return f'{time_s // 3600}:{time_s // 60}:{time_s % 60}.{time_ms % 1000}'


def test_convert_readable(ms):
    return timeit.timeit(f'convert_readable({ms})', setup='from __main__ import convert_readable', number=100000)


def test_convert_readable_str(ms):
    return timeit.timeit(f'convert_readable_str({ms})', setup='from __main__ import convert_readable_str', number=100000)


def test_timedelta(ms):
    return timeit.timeit(f'timedelta(milliseconds={ms})', setup='from datetime import timedelta', number=100000)


def test_to_datetime(ms):
    return timeit.timeit(f'pd.to_datetime({ms})', setup='import pandas as pd', number=100000)


def get_readable_time_v1(arr):
    pa.array(pd.to_datetime(pd.Series(arr), unit='ms'))


def get_readable_time_v2(arr):
    pd.Series(arr).apply(pd.to_datetime)


def get_readable_time_v3(arr):
    np.vectorize(pd.to_datetime)(arr)


def get_readable_time_v4(arr):
    pd.to_datetime(pd.Series(arr), unit='ms')


def get_readable_time_v4_micro(arr_us):
    return pd.to_datetime(pd.Series(arr_us), unit='us')


def get_readable_time_optimized_delta(arr_us):
    return pd.to_timedelta(pd.Series(arr_us), unit='us')


def get_readable_time_v5(arr):
    pd.to_datetime(arr)


def get_readable_time_v6(arr):
    convert_readable_str(pd.Series(arr))


def get_readable_time_v7(arr):
    convert_readable_str(arr)


def get_readable_time_v8(arr):
    pd.Series(arr).apply(lambda t: timedelta(milliseconds=t))


def get_readable_time_v9(arr):
    np.vectorize(lambda t: timedelta(milliseconds=float(t)))(arr)


def test_time_conversions_arr(sz, stmt, num=3):
    for i in range(1, 10):
        if i not in [2, 3, 8]:
            print(f'Testing version {i}: ', end='')
            print(min(timeit.Timer(f'get_readable_time_v{i}(arr)',
                        setup=f'import numpy as np; import pandas as pd; import pyarrow as pa; from __main__ import get_readable_time_v{i}; {stmt}')
                        .repeat(10, num)))


def measure_time_conversion_us(sz, num=10):
    return min(timeit.Timer(f'get_readable_time_v4_micro(a_us)',
                setup=f'import numpy as np; a_us = (np.arange({sz}) * 500.0).astype(np.int64); from __main__ import get_readable_time_v4_micro')
                .repeat(10, num))


if __name__ == "__main__":
    # print(sz / 3600 / 2000)  # Time duration in hours

    # print(test_convert_readable(ms_rand))
    # print(test_convert_readable_str(ms_rand))
    # print(test_timedelta(ms_rand))
    # print(test_to_datetime(ms_rand))
    # print(sys.getsizeof(convert_readable(ms_rand)))
    # print(sys.getsizeof(convert_readable_str(ms_rand)))

    # a = np.linspace(0, size - 1, num=size)
    # a = np.arange(size)

    # str_make_arange = f'arr = np.arange({size})'
    # str_make_linspace = f'arr = np.linspace(0, {size}-1, num={size})'
    # str_make_linspace_f = f'arr = np.linspace(0, {size}-1, num={size}) / 2'
    # test_time_conversions_arr(size, str_make_linspace)

    a_us = np.arange(size)
    factor = int((10 ** 6) / sample_rate)
    print(factor)
    print(10 ** 6 / sample_rate)
    # arr = a_us * 500
    a_mult_int = a_us * 500
    a_mult_flt = a_us * 500.0
    print(a_mult_int.dtype)
    print(a_mult_flt.dtype)
    # print(get_readable_time_v4_micro(arr))
    a_us_optimize = (np.arange(size) * (10 ** 6) / sample_rate).astype(np.int64)

    print(measure_time_conversion_us(size))
