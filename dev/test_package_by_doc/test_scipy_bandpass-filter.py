from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt

from ecg_record import EcgRecord

from icecream import ic


def bandpass_filter(data, low, high, fq, order=2):
    nyq = 0.5 * fq
    low /= nyq
    high /= nyq
    r = butter(order, [low, high], btype='bandpass')
    return lfilter(*r, data)


if __name__ == "__main__":
    rec = EcgRecord.example()
    strt, end = 0, 10000
    y = rec.get_ecg_samples(0, strt, end)
    x = rec.get_time_values(strt, end)

    for order in range(1, 7):
        plt.figure(figsize=(16, 9))
        plt.plot(x, y, label='ori')

        # order
        rang = [0.5, 40]
        y_filt = bandpass_filter(y, *rang, 2000, order=order)
        plt.plot(x, y_filt, label=f'filtered, order={order}')
        plt.legend(loc='lower left')
        plt.savefig(f'bandpass filter, range={rang}, order={order}.png', dpi=300)
        plt.show()




