import numpy as np
import pandas as pd
import pyarrow as pa
import timeit
from datetime import timedelta
import sys

size = 3632348
ms_rand = 1497625.5  # A typical float passed into time conversion


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


def test_np_arange(sz):
    return timeit.timeit(f'np.arange({sz})', setup='import numpy as np', number=1000)


def test_np_linspace(sz):
    return timeit.timeit(f'np.linspace(0, {sz-1}, num={sz})', setup='import numpy as np', number=1000)


def get_readable_time_v1(arr):
    pa.array(pd.to_datetime(pd.Series(arr), unit='ms'))


def get_readable_time_v2(arr):
    pd.Series(arr).apply(pd.to_datetime)


def get_readable_time_v3(arr):
    arr.apply(pd.to_datetime)


def get_readable_time_v4(arr):
    pd.Series(arr).to_datetime()


def get_readable_time_v5(arr):
    arr.to_datetime()


def get_readable_time_v6(arr):
    pd.Series(arr).convert_readable_str()


def get_readable_time_v7(arr):
    arr.convert_readable_str()


def test_time_conversions(sz, num=3):
    for i in range(1, 8):
        print(min(timeit.Timer(f'get_readable_time_v{i}(arr)',
                    setup=f'import numpy as np; import pandas as pd; import pyarrow as pa; from __main__ import get_readable_time_v{i}; arr = np.arange({sz})')
                    .repeat(10, num)))


if __name__ == "__main__":
    # print(sz / 3600 / 2000)  # Time duration in hours

    print(test_convert_readable(ms_rand))
    print(test_convert_readable_str(ms_rand))
    print(test_timedelta(ms_rand))
    print(test_to_datetime(ms_rand))
    print(sys.getsizeof(convert_readable(ms_rand)))
    print(sys.getsizeof(convert_readable_str(ms_rand)))

    # print(test_np_arange(size))
    # print(test_np_linspace(size))
    # a = np.linspace(0, size - 1, num=size)
    # a = np.arange(size)

    test_time_conversions(size)
