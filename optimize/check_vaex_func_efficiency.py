import vaex as vx
import timeit

import ecgrecord
from test_package_by_doc.explore_vaex_basics import vx_df_eg


def test_np_join():
    setup = "import ecgrecord; ecg_record, seg, lead = ecgrecord.ECGRecord.example()"
    stmt = "ecg_record.join_lead(0)"
    return timeit.timeit(stmt, setup, number=100)


def test_vx_from_dict():
    setup = "import vaex as vx; import ecgrecord; ecg_record, seg, lead = ecgrecord.ECGRecord.example(); arr_join = ecg_record.join_lead(0); d = {'ecg_mag': arr_join}"
    stmt = "ecg_df = vx.from_dict(d)"
    return timeit.timeit(stmt, setup, number=10000)


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


if __name__ == "__main__":
    df = vx_df_eg()
    # print(df.__dict__)
    # print(df.__dict__.keys())

    ecg_record, seg, lead = ecgrecord.ECGRecord.example()
    # keys = ecg_record.get_segment_keys()
    # print(keys, type(keys))
    arr_single = lead.get_ecg_values()
    # print(len(arr_single))
    arr_join = ecg_record.join_lead(0)
    # print(len(arr_join))
    # print(len(arr_join) / len(arr_single))
    d = {'ecg_mag': arr_join}
    # print(type(arr))
    ecg_df = vx.from_dict(d)
    # print(sys.getsizeof(ecg_df))

    print(test_np_join())
    print(test_vx_from_dict())
    # print(sizeof_fmt(arr_join.nbytes))

    # print(seg.get_time_axis())


