import numpy as np
import pandas as pd
from datetime import timedelta
import sys

from optimize.optimize_time_conversion import ms_rand

if __name__ == "__main__":
    delta = timedelta(days=50, seconds=27, microseconds=10, milliseconds=29000, minutes=5, hours=8, weeks=2)
    print(delta)
    t = timedelta(milliseconds=ms_rand)  # So it can work on a float
    print(sys.getsizeof(t))
    print(t, type(t))
    t2 = timedelta(seconds=100)
    print(t2)

    print(np.timedelta64(23, 'ms'))
    print(np.timedelta64(int(ms_rand), 'ms'))

    print(pd.to_datetime(1, unit='ns'))  # 10 to power of -9, nanosecond ns
    print(pd.to_datetime(1, unit='us'))  # 10 to power of -6, microsecond us



