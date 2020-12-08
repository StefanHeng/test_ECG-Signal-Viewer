import numpy as np
import pandas as pd

import plotly.graph_objs as go

from math import floor
from copy import deepcopy


class EcgPlot:
    """Handles plotting for a particular `record`, or surgery.
    """

    D_RNG_INIT = [
        [0, 100000],  # First 50s, given 2000 sample_rate
        [-4000, 4000]  # -4V to 4V
    ]

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
    DEFAULT_BG = 'rgba(229, 236, 246, 0.8)'

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
        ecg_vals = self.recr.get_samples(idx_lead, strt, end, sample_factor)
        # Take the size of array,
        # for integer division almost never perfectly match the size returned by advanced slicing
        sample_counts = np.linspace(strt, end, num=ecg_vals.shape[0])
        return self.to_time_axis(sample_counts), ecg_vals

    def get_fig(self, idx_lead, strt, end):
        # logger.info(f'sample_counts of size {sample_counts.shape[0]} -> {sample_counts}')
        # logger.info(f'ecg_vals of size {ecg_vals.shape[0]} -> {ecg_vals}')
        time_vals, ecg_vals = self.get_xy_vals(idx_lead, strt, end)
        # print(f'in get fig: with [{time_vals.shape}] x vals and [{ecg_vals.shape}] y vals')
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
                    size=1),
            )],
            layout=dict(
                # uirevision=self.PRESERVE_UI_STATE,
                plot_bgcolor=self.DEFAULT_BG,
                dragmode='pan',
                margin=dict(l=40, r=0, t=0, b=17),  # Less than default margin, effectively cropping out whitespace
                hoverdistance=0,
                hoverinfo=None,
                xaxis=xaxis_config,
                yaxis=yaxis_config
            )
        )

    def get_thumb_fig(self, idx_lead):
        time_vals, ecg_vals = self.get_xy_vals(idx_lead, 0, self.recr.num_sample_count())
        xaxis_config = dict(
            # type='date',
            rangeslider=dict(
                visible=True,
                bgcolor=self.DEFAULT_BG,
                # bordercolor='black',
                thickness=1
            )
        )
        fig = go.Figure(
            data=[dict(x=time_vals, y=ecg_vals)],
            layout=dict(
                margin=dict(l=0, r=0, t=0, b=200),  # Hence same width and relative placement as the actual figure
                xaxis=xaxis_config,
            )
        )
        # This `range` is different than the range argument in Figure creation, which crops off data
        fig['layout']['xaxis']['range'] = [
            self.recr.sample_count_to_time_str(self.D_RNG_INIT[0][0]),
            self.recr.sample_count_to_time_str(self.D_RNG_INIT[0][1])
        ]
        return fig
        # return dict(
        #     data=[dict(x=time_vals, y=ecg_vals)],
        #     layout=dict(
        #         margin=dict(l=0, r=0, t=0, b=200),  # Hence same width and relative placement as the actual figure
        #         xaxis=xaxis_config,
        #     )
        # )

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
