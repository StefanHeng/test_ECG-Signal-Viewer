import matplotlib.pyplot as plt

from ecg_record import EcgRecord
from ecg_marker import EcgMarker

from random import randint

from icecream import ic


if __name__ == '__main__':
    rec = EcgRecord.example()
    mkr = EcgMarker(rec)
    idx_lead = 0
    # mkr.export(idx_lead)

    # Sanity check
    strt = randint(0, rec.COUNT_END)
    end = 8000 + strt
    x = rec.get_time_values(strt, end)
    y = rec.get_ecg_samples(idx_lead, strt, end)
    ic(strt, end)

    plt.figure(figsize=(18, 6), constrained_layout=True)
    plt.plot(x, y, label='Data, ori', marker='o', markersize=0.3, linewidth=0.25)
    plt.plot(x, mkr.bandpass_filter(y), label='Data, filtered', marker='o', markersize=0.3, linewidth=0.25)
    for idx_r in rec.r_peak_indices(strt, end):
        plt.axvline(x=rec.count_to_pd_time(strt + idx_r), label='R peak', lw=0.5, c='r')
        plt.axhline(y=y[idx_r], label='Volt at r peak', lw=0.5, c='g')

    handles, labels = plt.gca().get_legend_handles_labels()  # Distinct labels
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    plt.show()

