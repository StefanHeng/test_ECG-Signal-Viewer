import numpy as np

from scipy.signal import butter, lfilter, hilbert
from ecgdetectors import Detectors

from data_link import *
from dev_helper import record_nm
from ecg_record import EcgRecord

from icecream import ic


class EcgMarker:
    """ Given a `EcgRecord`, detects R peak, QRS range locations, Filtering, in terms of `EcgRecord` sample counts.

    Write those annotations to a file for `EcgApp` usage.

    References
    ----------
    .. [1] A. Illanes-Manriquez and Q. Zhang,
            "An algorithm for robust detection of QRS onset and offset in ECG signals,"
            2008 Computers in Cardiology, Bologna, Italy, 2008, pp. 857-860,
            doi: 10.1109/CIC.2008.4749177.
    """

    SCH_WD_MS = 100  # Half of range to look for optimal R peak, in ms
    FTR_TMPL = dict(  # Template filter passes
        on=(0.5, 40),
        off=(5, 30),
        display=(0.05, 40)
    )

    def __init__(self, record):
        """
        :param record: An instance of `EcgRecord`
        """
        self.rec = record

        self.dctr = Detectors(2000)
        self.SCH_WD_CNT = int(self.SCH_WD_MS * self.rec.spl_rate / 1000)

    def bandpass_filter(self, ecg_vals, low=-1, high=-1, order=1, template='off'):
        """
        Takes low and high pass frequency if `template` unspecified.

        :param ecg_vals: ECG values, unsampled, by sample rate of the `EcgRecord` instance
        :param low: Low pass frequency
        :param high:  High pass frequency
        :param order: As order in filter
        :param template: Low & high pass frequency template values
        :return: Filtered ECG values

        .. note:: On template, 'on' for QRS onset detection with [0.5, 40]Hz,
        'off' for QRS offset detection with [5, 30]Hz
        """
        if low == -1 and high == -1:  # Code specified
            low, high = self.FTR_TMPL[template]
        nyq = 0.5 * self.rec.spl_rate
        low /= nyq
        high /= nyq
        r = butter(order, [low, high], btype='bandpass')
        return lfilter(*r, ecg_vals)

    def r_peak_indices(self, idx_lead, ecg_vals):
        indices = np.array(self.dctr.two_average_detector(ecg_vals))
        func = np.argmin if self.rec.is_negative[idx_lead] else np.argmax
        n = ecg_vals.shape[0]
        indices_offset = np.vectorize(lambda idx: func(ecg_vals[
                                max(0, idx - self.SCH_WD_CNT):
                                min(n, idx + self.SCH_WD_CNT)
                             ]))(indices)
        return indices + indices_offset - self.SCH_WD_CNT

    @staticmethod
    def envelope(ecg_vals):
        """ Returns envelope of the ECG signal

        :param ecg_vals: Filtered ECG signal
        """
        return np.abs(hilbert(ecg_vals))  # Returns magnitude of complex number

    @staticmethod
    def example(record=EcgRecord(DATA_PATH.joinpath(record_nm))):
        return EcgMarker(record)
