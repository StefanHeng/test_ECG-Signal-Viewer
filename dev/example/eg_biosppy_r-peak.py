from biosppy import storage
from biosppy.signals import ecg

from ecg_record import EcgRecord

import joblib

if __name__ == '__main__':
    rec = EcgRecord.example()
    strt, end = 0, 10000
    y = rec.get_ecg_samples(0, strt, end)
    out = ecg.ecg(signal=y, sampling_rate=1000., show=True)

