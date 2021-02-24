from biosppy import storage
from biosppy.signals import ecg

from icecream import ic

import joblib

from ecg_record import EcgRecord


if __name__ == '__main__':
    rec = EcgRecord.example()
    strt, end = 0, 10000
    y = rec.get_ecg_samples(0, strt, end)
    ic(ecg.engzee_segmenter(y, sampling_rate=2000))

