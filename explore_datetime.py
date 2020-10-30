from datetime import timedelta
import sys

from optimize_time_conversion import ms_rand

if __name__ == "__main__":
    delta = timedelta(days=50, seconds=27, microseconds=10, milliseconds=29000, minutes=5, hours=8, weeks=2)
    print(delta)
    t = timedelta(milliseconds=ms_rand)
    print(sys.getsizeof(t))
    print(t, type(t))
    t2 = timedelta(seconds=100)
    print(t2)

