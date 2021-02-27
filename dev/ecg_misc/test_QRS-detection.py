import numpy as np
import matplotlib.pyplot as plt

from icecream import ic

from ecg_record import EcgRecord
from ecg_marker import EcgMarker


if __name__ == '__main__':
    rec = EcgRecord.example()
    marker = EcgMarker(rec)
    strt, end = rec.DEBUG_get_rand_range(N=6000)
    # idx_lead = 2  # `V1` is good choice to run QRS detection
    idx_lead = 0  # Empirically check values, which looks like shape of ECG signals the most
    x = rec.get_time_values(strt, end)
    y = rec.get_ecg_samples(idx_lead, strt, end)
    # y = np.linspace(-10, 10, num=101)
    y_filtered = marker.bandpass_filter(y)
    y_envelope = marker.envelope(y_filtered)
    ic(y)
    ic(y_filtered)
    ic(y_envelope)

    plt.figure(figsize=(18, 6))
    plt.plot(x, y, label='ori', lw=1)
    plt.plot(x, y_filtered, label='filtered', lw=1)
    plt.plot(x, y_envelope, lw=1, label='envelope')
    plt.legend(loc=0)
    plt.show()
