import pandas as pd
from bisect import bisect_left

from dash_extensions.snippets import send_data_frame

from icecream import ic


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
        def find_row(count):
            """ Given a count, find which row index would the count be in """
            return (count - strt) // step
        step = 1  # Grabs all samples by default
        if end - strt > self._MAX_EXP_COUNT:
            step = (end - strt) // self._MAX_EXP_COUNT
        df = pd.DataFrame(
            self._merge(
                {'time': self.rec.get_time_values_delta(strt, end, step)},
                {self.rec.lead_nms[idx]: self.rec.get_ecg_samples(idx, strt, end, step) for idx in idxs_lead}
            )
        )
        t = 'tag'
        df[t] = ''  # Append static annotation/`tag`s as the next column
        idx_strt, idx_end = self.rec.get_tag_indices(strt, end)
        for i in range(idx_strt, idx_end):
            typ, t_ms, _ = self.rec.tags[i]
            row = find_row(self.rec.ms_to_count(t_ms))
            ori = df.at[row, t]
            df.at[row, t] = typ if ori == '' else f'{ori}; {typ}'
        df['comment'] = ''  # Append manual annotations/`comment`s column

        title = f'ECG export, idxs {idxs_lead}, [{self.rec.count_to_str(strt)}-{self.rec.count_to_str(end)}]'
        df.style.set_caption(title)
        return send_data_frame(df.to_csv, filename=f'{title}.csv')
