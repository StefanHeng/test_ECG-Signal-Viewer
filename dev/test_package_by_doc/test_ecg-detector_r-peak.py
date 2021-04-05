from ecgdetectors import Detectors
import matplotlib.pyplot as plt

from random import randint

from ecg_record import EcgRecord
from ecg_marker import EcgMarker

from icecream import ic


if __name__ == "__main__":

    rec = EcgRecord.example()
    # strt, end = 10000, 20000
    # strt, end = 0, 10000
    # strt, end = 1432494, 1454324
    strt = randint(0, rec.COUNT_END)
    end = 8000 + strt
    idxs_lead_pos = list(filter(lambda i: not rec.is_negative[i], list(range(len(rec.is_negative)))))
    idxs_lead_neg = list(filter(lambda i: rec.is_negative[i], list(range(len(rec.is_negative)))))
    idx_lead = 7
    # idx_lead = 14  # Negative lead
    y = rec.get_ecg_samples(idx_lead, strt, end)
    x = rec.get_time_values(strt, end)

    mkr = EcgMarker(rec)
    my_r_peaks = mkr.r_peak_indices(idx_lead, y)

    detectors = Detectors(2000)
    funcs = [
        detectors.hamilton_detector,
        detectors.christov_detector,
        detectors.engzee_detector,
        detectors.pan_tompkins_detector,
        detectors.swt_detector,
        detectors.two_average_detector
    ]

    plt.figure(figsize=(18, 6))
    plt.plot(x, y, label='Data, ori', marker='o', markersize=0.3, linewidth=0.25)
    plt.plot(x, mkr.bandpass_filter(y), label='Data, filtered', marker='o', markersize=0.3, linewidth=0.25)
    colors = ['b', 'g', 'r', 'c', 'm', 'y']

    for i, func in enumerate(funcs):
        if i == 5:
            for count in func(y):
                plt.axvline(x=rec.count_to_pd_time(count + strt), c=colors[i], lw=1, label='R peak, package')
    for count in my_r_peaks:
        plt.axvline(x=rec.count_to_pd_time(count + strt), c='purple', lw=1, label='R peak, optim')
    handles, labels = plt.gca().get_legend_handles_labels()  # Distinct labels
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    plt.show()
