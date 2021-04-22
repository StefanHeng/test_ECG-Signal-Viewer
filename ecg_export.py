import pandas as pd
# from bisect import bisect_left

from dash_extensions.snippets import send_data_frame

import json

from icecream import ic


class EcgExport:
    """ Handles export current lead channel and range of data on display to CSV """

    def __init__(self):
        self.rec = None
        self.cmts = None
        self._MAX_EXP_COUNT = None

    def set_record(self, record, comments):
        self.rec = record
        self.cmts = comments
        self._MAX_EXP_COUNT = self.rec.spl_rate * 2 * 60

    @staticmethod
    def _merge(d1, d2):  # Workaround for before python 3.9
        return {**d1, **d2}

    def export(self, strt, end, idxs_lead):
        """
        At maximum, allow users to export 2 minutes of data as a benchmark.

        If start and end values specified goes within 2 *2 min, all data within range are exported;
        otherwise, function still works but will take steps/samples of the data (due to integer division)

        Each comment is stored at the time stamp of sample count as a list element through JSOn string,
        each comment is a 5-element list of <x.center>, <y.center>, <x.0>, <y.0>, <msg>
        """
        def _find_row(count):
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
        df[t] = ''  # Append static annotation/`tag`s as the next column, across all leads
        idx_strt, idx_end = self.rec.get_tag_indices(strt, end)
        for i in range(idx_strt, idx_end):
            typ, t_ms, _ = self.rec.tags[i]
            row = _find_row(self.rec.ms_to_count(t_ms))
            ori = df.at[row, t]
            df.at[row, t] = typ if ori == '' else f'{ori}; {typ}'
        for idx_ld in idxs_lead:  # Dependent on each lead
            col_nm = f'comment_{self.rec.lead_nms[idx_ld]}'
            df[col_nm] = ''  # Append manual annotations/`comment`s column
            _, lst = self.cmts.get_comment_list([idx_ld], strt, end, verbose=True)
            # prev_count = -1
            # n_same = 0  # Number of comments at the same time stamp
            # lst_same = []
            # for cmt in lst:
            #     x_c, y_c, x0, y0, _, msg = cmt
            #     if x_c == prev_count:
            #         n_same += 1
            #         lst_same.append([x_c, y_c, x0, y0, msg])
            #     else:
            #         row = find_row(x_c)
            #     prev_count = x_c
            #     # Last comment at the same count

            def _get_comments():
                d = dict()
                for cmt in lst:
                    count = cmt[0]
                    # cmt = cmt[:4] + cmt[5:]  # Remove the lead index element
                    d_cmt = dict(
                        xc=str(self.rec.count_to_pd_delta(cmt[0])),
                        yc=cmt[1],
                        x0=str(self.rec.count_to_pd_delta(cmt[2])),
                        y0=cmt[3],
                        msg=cmt[-1]
                    )
                    if count in d:
                        d[count].append(d_cmt)
                    else:
                        d[count] = [d_cmt]
                return d

            for count, cmts in _get_comments().items():
                # ic(count, cmts)
                df.at[_find_row(count), col_nm] = json.dumps(cmts)

        title = f'ECG export, idxs {idxs_lead}, [{self.rec.count_to_str(strt)}-{self.rec.count_to_str(end)}]'
        df.style.set_caption(title)
        return send_data_frame(df.to_csv, filename=f'{title}.csv')
