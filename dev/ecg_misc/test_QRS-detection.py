import matplotlib.pyplot as plt

from icecream import ic

from ecg_record import EcgRecord
from ecg_marker import EcgMarker


if __name__ == '__main__':
    rec = EcgRecord.example()
    mkr = EcgMarker(rec)
    strt, end = rec.DEBUG_get_rand_range(N=6000)
    # idx_lead = 2  # `V1` is good choice to run QRS detection
    idx_lead = 0  # Empirically check values, which looks like shape of ECG signals the most
    x = rec.get_time_values(strt, end)
    y = rec.get_ecg_samples(idx_lead, strt, end)
    # y_noc = mkr.notch_filter(y, quality_factor=6)
    y_filtered = mkr.bandpass_filter(y, template='off')
    # y_filtered_noc = mkr.notch_filter(y_filtered, quality_factor=6000)
    y_envelope = mkr.envelope(y_filtered)
    # y_envelope_noc = mkr.envelope(y_filtered_noc)
    ic(y)
    ic(y_filtered)
    ic(y_envelope)

    plt.figure(figsize=(18, 6))
    plt.plot(x, y, label='Signal, ori',  marker='o', markersize=0.3, linewidth=0.25)
    plt.plot(x, y_filtered, label='Signal, filtered', marker='o', markersize=0.3, linewidth=0.25)
    # plt.plot(x, y_noc, label='notch filter only', lw=1)
    # plt.plot(x, y_filtered_noc, label='filtered, with notch', lw=1)
    plt.plot(x, y_envelope, label='Signal, envelope', marker='o', markersize=0.3, linewidth=0.25)
    # plt.plot(x, y_envelope_noc, lw=1, label='envelope, with notch')

    for idx_peak in mkr.r_peak_indices(idx_lead, y):
        plt.axvline(x=rec.count_to_pd_time(idx_peak + strt), c='r', lw=0.5, label='R peak')
        idx = mkr.get_qrs_offset(y, idx_peak)
        plt.axvline(x=rec.count_to_pd_time(idx + strt), c='purple', lw=0.5, label='QRC offset')

    handles, labels = plt.gca().get_legend_handles_labels()  # Distinct labels
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    # plt.legend(loc=0)
    plt.show()
