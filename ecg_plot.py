import numpy as np
import pandas as pd
import plotly.graph_objs as go
# import plotly.express as px

from math import floor

from ecg_record import *

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('dev')


class EcgPlot:
    """Handles plotting among a single `record`, or surgery.
    """

    def __init__(self, path):
        self.ecg_record = EcgRecord(path)
        # Ad-hoc values for now, in the future should be calculated from device info
        # Default starting point, in the future should be retrieved from user
        self._display_width = 100  # in rem, display_width * display_scale_t gets the number of points to render
        self._display_scale_t = 20  # #continuous time stamps to display in 1rem
        self._display_scale_ecg = 20  # magnitude of ecg in a 1rem
        # A valid range has values [0, sum of all samples across the entire ecg_record)
        # Inclusive start and end
        self._display_range = (0, 10000)  # based on #samples, one-to-one correspondence with time by `sample_rate`

    def get_plot(self, idx_lead):
        """
        :param idx_lead: index of lead
        :return: plotly line plot based on current display range

        .. seealso:: `ecg_record.get_samples`
        """
        strt, end = self._display_range
        # determine if optimization is needed for large sample_range
        sample_factor = floor((end - strt + 1) / (self._display_width * self._display_scale_t))
        if sample_factor >= 10:
            sample_counts = np.linspace(strt, end, num=(end-strt + 1) // sample_factor)
            ecg_vals = self.ecg_record.get_samples(idx_lead, self._display_range, sample_factor)
        else:
            # No need to take steps for small sample_factor
            sample_counts = np.arange(strt, end+1)
            ecg_vals = self.ecg_record.get_samples(idx_lead, self._display_range)
        logger.info(f'sample_counts of size {sample_counts.shape[0]} -> {sample_counts}')
        logger.info(f'ecg_vals of size {ecg_vals.shape[0]} -> {ecg_vals}')

        fig = go.Figure(
            data=go.Scatter(
                x=self.get_time_axis(sample_counts, 2000),  # TODO: sample_rate uniform across all files?
                y=ecg_vals
            )
        )

        fig.update_layout(
            xaxis_title="time(s)",
            yaxis_title="ECG Signal Magnitude(mV)"
        )

        return fig

    @staticmethod
    def get_time_axis(arr, sample_rate):
        """
        :return: Evenly spaced 1D array of incremental time stamps in microseconds
        """
        factor = 10**6 / sample_rate
        if floor(factor) == factor:  # Is an int
            arr *= int(factor)
        else:
            arr = (arr * factor).astype(np.int64)
        # Converted to time in microseconds as integer, drastically raises efficiency while maintaining precision
        return pd.to_datetime(pd.Series(arr), unit='us')

    @staticmethod
    def example(idx_lead=0):
        import pathlib
        ecg_plot = EcgPlot(DATA_PATH.joinpath(selected_record))
        return ecg_plot.get_plot(idx_lead)
