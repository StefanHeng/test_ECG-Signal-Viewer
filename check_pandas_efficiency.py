import pandas as pd
import sys
import timeit

from check_vaex_func_efficiency import sizeof_fmt

t_in_ms = 101242323432.5  # arbitrary value to be used as timestamp, for 2000 sample rate
t_in_s = t_in_ms / 1000


def test_pd_to_timestamp():
    setup = "import ecgrecord; ecg_record, seg, lead = ecgrecord.ECGRecord.example()"
    stmt = "seg.get_time_axis()"
    return timeit.timeit(stmt, setup, number=2)


if __name__ == "__main__":
    print(sys.getsizeof(t_in_ms))
    sz_int = sys.getsizeof(t_in_s)
    print(sz_int)
    tstamp_s = pd.to_datetime(t_in_s, unit='s')
    tstamp_ms = pd.to_datetime(t_in_ms, unit='ms')
    print(sys.getsizeof(tstamp_s))
    sz_tstamp = sys.getsizeof(tstamp_ms)
    print(sz_tstamp)

    sz_single_lead = 3632348
    print(sizeof_fmt(sz_int * sz_single_lead))
    print(sizeof_fmt(sz_tstamp * sz_single_lead))

    print(test_pd_to_timestamp())



