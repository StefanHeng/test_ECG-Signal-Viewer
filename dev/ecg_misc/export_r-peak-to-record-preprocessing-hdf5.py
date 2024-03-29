import matplotlib.pyplot as plt

from ecg_record import EcgRecord
from ecg_marker import EcgMarker

from random import randint

from icecream import ic


def sanity_check():
    strt = randint(0, rec.COUNT_END)
    end = 8000 + strt
    x = rec.get_time_values(strt, end)
    y = rec.get_ecg_samples(idx_lead, strt, end)
    ic(strt, end)

    plt.figure(figsize=(18, 6), constrained_layout=True)
    plt.plot(x, y, label='Data, ori', marker='o', markersize=0.3, linewidth=0.25)
    plt.plot(x, mkr.bandpass_filter(y), label='Data, filtered', marker='o', markersize=0.3, linewidth=0.25)
    vals_r = rec.r_peak_vals(idx_lead, strt, end)
    ic(vals_r)
    for i, idx_r in enumerate(rec.r_peak_indices(strt, end)):
        plt.axvline(x=rec.count_to_pd_time(strt + idx_r), label='R peak', lw=0.5, c='r')
        plt.axhline(y=vals_r[i], label='Volt at r peak', lw=0.5, c='g')

    handles, labels = plt.gca().get_legend_handles_labels()  # Distinct labels
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    plt.show()


if __name__ == '__main__':
    rec = EcgRecord.example()
    mkr = EcgMarker(rec)
    idx_lead = 3
    # mkr.export(idx_lead)
    #
    sanity_check()

