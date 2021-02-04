import pandas as pd

from dash_extensions.snippets import send_data_frame


class EcgExport:
    """ Handles export current lead channel and range of data on display to CSV """

    def __init__(self):
        self.rec = None
        self._MAX_EXP_COUNT = None

    def set_record(self, record):
        self.rec = record
        self._MAX_EXP_COUNT = self.rec.spl_rate * 2 * 60

    @staticmethod
    def _merge(d1, d2):  # Workaround until python 3.9
        return {**d1, **d2}

    def export(self, strt, end, idxs_lead):
        """
        At maximum, allow users to export 2 minutes of data as a benchmark.

        If start and end values specified goes within 2 *2 min, all data within range are exported;
        otherwise, function still works but will take steps/samples of the data (due to integer division)

        """
        step = 1
        if end - strt > self._MAX_EXP_COUNT:
            step = (end - strt) // self._MAX_EXP_COUNT
        t = 'time'
        df = pd.DataFrame(
            self._merge({t: self.rec.get_time_values_delta(strt, end, step)}, {
                self.rec.lead_nms[idx]: self.rec.get_ecg_samples(idx, strt, end, step) for idx in idxs_lead
            })
            # columns=[t] + [self.rec.lead_nms[idx] for idx in idxs_lead],
            # data=[self.rec.get_time_values(strt, end, step)] + [
            #     self.rec.get_ecg_samples(idx, strt, end, step) for idx in idxs_lead
            # ])
        )
        title = f'ECG export, idxs {idxs_lead}, [{self.rec.count_to_str(strt)}-{self.rec.count_to_str(end)}]'
        df.style.set_caption(title)
        return send_data_frame(df.to_csv, filename=f'{title}.csv')

