import numpy as np

from scipy.signal import butter, lfilter, hilbert, iirnotch
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

    R_SCH_WD_MS = 100  # Half of range to look for optimal R peak, in ms
    FTR_TMPL = dict(  # Template filter passes
        on=(0.5, 40),
        off=(5, 30),
        display=(0.05, 40)
    )

    MAX_QRS_MS = 200  # Maximum size of QRS complex that would be encountered in practice, in ms
    QRS_ON_MS = 300  # QRS onset search window width
    QRS_OF_MS = 150  # QRS offset search window width

    def __init__(self, record):
        """
        :param record: An instance of `EcgRecord`
        """
        self.rec = record

        self.r_peak_detector = Detectors(self.rec.spl_rate)
        self.R_SCH_WD_CNT = self.rec.ms_to_count(self.R_SCH_WD_MS)
        # QRS internal calculations done with sample count instead of time
        self.MAX_QRS_CNT = self.rec.ms_to_count(self.MAX_QRS_MS)
        self.QRS_SCH_WD_OFST = np.array([  # Start and end offset values for onset and offset
            [-self.rec.ms_to_count(self.QRS_ON_MS), 0],
            [0, self.rec.ms_to_count(self.QRS_OF_MS)]
        ])

    def bandpass_filter(self, signal, low=-1, high=-1, order=1, template='off'):
        """
        Takes low and high pass frequency if `template` unspecified.

        Expect unsampled, by sample rate of the `EcgRecord` instance

        :param signal: Signal amplitude values.
        :param low: Low pass frequency
        :param high:  High pass frequency
        :param order: As order in filter
        :param template: Low & high pass frequency template values
        :return Bandpass filtered signal values

        .. note:: On template, 'on' for QRS onset detection with [0.5, 40]Hz,
        'off' for QRS offset detection with [5, 30]Hz
        """
        if low == -1 and high == -1:  # Code specified
            low, high = self.FTR_TMPL[template]
        nyq = 0.5 * self.rec.spl_rate
        low /= nyq
        high /= nyq
        r = butter(order, [low, high], btype='bandpass')
        return lfilter(*r, signal)

    def notch_filter(self, signal, fqs=60, quality_factor=30):
        """
        :param signal: Amplitude values
        :param fqs: The frequency to remove
        :param quality_factor: Per `scipy.signal.iirnotch`
        :return Notch filtered signal values
        """
        b, a = iirnotch(fqs, quality_factor, self.rec.spl_rate)
        return lfilter(b, a, signal)

    def r_peak_indices(self, idx_lead, ecg_vals):
        indices = np.array(self.r_peak_detector.two_average_detector(ecg_vals))
        func = np.argmin if self.rec.is_negative[idx_lead] else np.argmax
        n = ecg_vals.shape[0]
        indices_offset = np.vectorize(lambda idx: func(ecg_vals[
                                max(0, idx - self.R_SCH_WD_CNT):
                                min(n, idx + self.R_SCH_WD_CNT)
                             ]))(indices)
        return indices + indices_offset - self.R_SCH_WD_CNT

    @staticmethod
    def envelope(ecg_vals):
        """ Returns envelope of the ECG signal

        :param ecg_vals: Filtered ECG signal
        """
        return np.abs(hilbert(ecg_vals))  # Returns magnitude of complex number

    def get_qrs_offset(self, ecg_vals, idx_peak):
        """
        :return QRS offset index relative to `ecg_vals`
        """
        envelope = self.envelope(self.bandpass_filter(ecg_vals, template='off'))
        idxs = np.arange(*(self.QRS_SCH_WD_OFST[1] + idx_peak))
        s2 = idx_peak + self.QRS_SCH_WD_OFST[1][0] + np.argmax(
            np.vectorize(lambda idx: self._get_area_indicator(envelope, idx, self.MAX_QRS_CNT))(idxs)
        )  # Absolute index relative to `ecg_vals`
        width = s2 - idx_peak + 1
        return idx_peak + self.QRS_SCH_WD_OFST[1][0] + np.argmax(
            np.vectorize(lambda idx: self._get_area_indicator(envelope, idx, width))(idxs)
        )  # Search through the same ending indices, but with different width

    @staticmethod
    def _get_area_indicator(envelope, idx, width):
        """
        Require: idx - width + 1 >= 0

        :return: Area from `idx`-`width`+1 to `idx` inclusive if requirement met, else -1
        """
        if idx - width + 1 >= 0:
            # Inclusive or not no difference, since the last value inclusive is 0 anyway
            return np.sum(envelope[idx - width + 1:idx] - envelope[idx])
        else:
            return -1  # An int to be compatible with np.ndarray

    @staticmethod
    def example(record=EcgRecord(DATA_PATH.joinpath(record_nm))):
        return EcgMarker(record)
