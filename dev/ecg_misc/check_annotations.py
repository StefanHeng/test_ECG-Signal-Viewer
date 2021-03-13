import pandas as pd

from ecg_record import EcgRecord

if __name__ == "__main__":
    rec = EcgRecord.example()
    ann = rec.tags
    # for i in range(2, len(ann)):
    #     print(ann[i])
    for a in ann:
        typ, time, text = a
        # print(pd.to_timedelta(time, unit='ms'))

    tms = 'time_ms'
    strt_ms = ann[0][1]
    end_ms = ann[-1][1]
    print(pd.to_timedelta(end_ms, unit='ms'))
    print(pd.to_timedelta(end_ms - strt_ms, unit='ms'))  # Okay, so range is correct

    print(rec.count_to_pd_time(rec.COUNT_END))
    print(rec.count_to_pd_time(rec.ms_to_count(end_ms)))

    print(rec.count_to_pd_time(rec.ms_to_count(4074167)))

    print(rec.count_to_pd_time(4107669))
