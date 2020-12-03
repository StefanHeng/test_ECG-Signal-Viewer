import numpy as np
import pandas as pd

from math import floor
from copy import deepcopy


class EcgPlot:
    """Handles plotting for a particular `record`, or surgery.
    """

    # Ad-hoc values for now, in the future should be calculated from device info
    # Default starting point, in the future should be retrieved from user
    _DISPLAY_WIDTH = 40  # in rem, display_width * display_scale_t gets the number of points to render
    _DISPLAY_SCALE_T = 20  # #continuous time stamps to display in 1rem
    _DISPLAY_SCALE_ECG = 20  # magnitude of ecg in a 1rem
    SP_RT_READABLE = 125  # Sufficient frequency (Hz) for human differentiable graphing

    PRESERVE_UI_STATE = True  # Arbitrarily picked value
    COLOR_PLOT = '#6AA2F9'  # Default blue by plotly
    PRIMARY = '#FCA912'
    SECONDARY = '#2C8595'
    SECONDARY_2 = '#80B6BF'
    GRAY_0 = '#808080'  # Gray

    def __init__(self, record, parent):
        self.recr = record
        self.parn = parent
        self.min_sample_step = self.recr.spl_rate // self.SP_RT_READABLE
        # Multiplying factor for converting to time in microseconds
        self.fac_to_us = 10 ** 6 / self.recr.spl_rate

    def get_xy_vals(self, idx_lead, strt, end):
        """
        :return: plotly line plot's x, y data points, based on current display range

        .. seealso:: `ecg_record.get_samples`
        """
        # Always take data as samples instead of entire channel, sample at at least increments of min_sample_step
        sample_factor = max(self._get_sample_factor(strt, end), self.min_sample_step)
        sample_counts = np.linspace(strt, end, num=(end - strt + 1) // sample_factor)
        return self.to_time_axis(sample_counts), self.recr.get_samples(idx_lead, strt, end, sample_factor)

    def get_fig(self, idx_lead, strt, end):
        # logger.info(f'sample_counts of size {sample_counts.shape[0]} -> {sample_counts}')
        # logger.info(f'ecg_vals of size {ecg_vals.shape[0]} -> {ecg_vals}')
        time_vals, ecg_vals = self.get_xy_vals(idx_lead, strt, end)
        xaxis_config = dict(
            showspikes=True,
            spikemode='toaxis',
            spikesnap='data',
            spikedash='dot',
            spikethickness=1,
            spikecolor=self.PRIMARY,
            linecolor=self.SECONDARY_2  # Axis color
        )
        yaxis_config = deepcopy(xaxis_config)
        return dict(
            data=[dict(
                x=time_vals,
                y=ecg_vals,
                mode='lines',
                marker=dict(
                    color=self.COLOR_PLOT,
                    size=10),
            )],
            layout=dict(
                uirevision=self.PRESERVE_UI_STATE,
                dragmode='pan',
                margin=dict(l=40, r=0, t=0, b=20),
                hoverdistance=0,
                hoverinfo=None,
                xaxis=xaxis_config,
                yaxis=yaxis_config
            )
        )

    def to_time_axis(self, sample_counts):
        """
        :return: Evenly spaced array of incremental time stamps in microseconds
        """
        if floor(self.fac_to_us) == self.fac_to_us:  # Is an int
            sample_counts *= int(self.fac_to_us)
        else:
            sample_counts = (sample_counts * self.fac_to_us).astype(np.int64)
        # Converted to time in microseconds as integer, drastically raises efficiency while maintaining precision
        return pd.to_datetime(pd.Series(sample_counts), unit='us')

    def _get_sample_factor(self, strt, end):
        # If showing too a small range, sample_factor which is incremental steps should be at least 1
        return max((end - strt + 1) // (self._DISPLAY_WIDTH * self._DISPLAY_SCALE_T), 1)
