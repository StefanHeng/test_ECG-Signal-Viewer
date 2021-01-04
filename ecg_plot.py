import numpy as np
import pandas as pd

import plotly.graph_objs as go

from math import floor
from copy import deepcopy


class EcgPlot:
    """Handles plotting for a particular `record`, or surgery.
    """

    DISP_RNG_INIT = [
        [0, 100000],  # First 50s, given 2000 sample_rate
        [-4000, 4000]  # -4V to 4V
    ]

    # Ad-hoc values for now, in the future should be calculated from device info
    # Default starting point, in the future should be retrieved from user
    _DISPLAY_WIDTH = 30  # in rem, display_width * display_scale_t gets the number of points to render
    _DISPLAY_SCALE_T = 10  # #continuous time stamps to display in 1rem
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
        self.rec = record
        self.parn = parent
        self.min_sample_step = self.rec.spl_rate // self.SP_RT_READABLE
        # Multiplying factor for converting to time in microseconds
        self.FAC_TO_US = 10 ** 6 / self.rec.spl_rate

    def get_xy_vals(self, idx_lead, strt, end):
        """
        :return: plotly line plot's x, y data points, based on current display range

        .. seealso:: `ecg_record.get_samples`
        """
        # Always take data as samples instead of entire channel, sample at at least increments of min_sample_step
        sample_factor = self.get_sample_factor(strt, end)
        ecg_vals = self.rec.get_samples(idx_lead, strt, end, sample_factor)
        # Take the size of array,
        # for integer division almost never perfectly match the size returned by advanced slicing
        sample_counts = np.linspace(strt, end, num=ecg_vals.shape[0])
        return self.to_time_axis(sample_counts), ecg_vals

    @staticmethod
    def _count_indexing_num(strt, end, step):
        """Counts the number of elements as result of numpy array indexing """
        num = (end - strt) // step
        if (end - strt) % step != 0:
            num += 1
        return num

    def get_x_vals(self, strt, end, sample_factor):
        sample_counts = np.linspace(strt, end, num=self._count_indexing_num(strt, end, sample_factor))
        return self.to_time_axis(sample_counts)

    def get_y_vals(self, idx_lead, strt, end, sample_factor):
        return self.rec.get_samples(idx_lead, strt, end, sample_factor)

    def get_fig(self, idx_lead, strt, end):
        # logger.info(f'sample_counts of size {sample_counts.shape[0]} -> {sample_counts}')
        # logger.info(f'ecg_vals of size {ecg_vals.shape[0]} -> {ecg_vals}')
        time_vals, ecg_vals = self.get_xy_vals(idx_lead, strt, end)
        xaxis_config = dict(
            # showspikes=True,
            # spikemode='toaxis',
            # spikesnap='data',
            # spikedash='dot',
            # spikethickness=1,
            # spikecolor=self.PRIMARY,
            # linecolor=self.SECONDARY_2  # Axis color
            # range=self.rec.get_range()
        )
        yaxis_config = dict(
            range=self.parn.ui.get_ignore_noise_range(ecg_vals)
        )
        return dict(
            data=[dict(
                x=time_vals,
                y=ecg_vals,
                mode='lines',
                line=dict(
                    color=self.SECONDARY,
                    width=0.5),
            )],
            layout=dict(
                plot_bgcolor='transparent',
                dragmode='pan',
                font=dict(size=10),
                margin=dict(l=45, r=30, t=0, b=15),  # Less than default margin, effectively cropping out whitespace
                hoverdistance=0,
                hoverinfo=None,
                xaxis=xaxis_config,
                yaxis=yaxis_config
            )
        )

    class Thumbnail:
        """ Encapsulates the plotly figure dummy used for global thumbnail preview

        Plot across the entire duration, with all channels selected
        """
        def __init__(self, record, parent):
            self.rec = record
            self.parn = parent
            self.strt = 0  # Stays unchanged, given a record
            self.end = self.rec.num_sample_count()
            self.sample_factor = self.parn.get_sample_factor(self.strt, self.end)
            self.x_vals = self.parn.get_x_vals(self.strt, self.end, self.sample_factor)
            self.fig = self._get_fig_skeleton()
            self.idxs_lead = []

        def _get_fig_skeleton(self):
            fig = go.Figure()
            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(
                    rangeslider=dict(
                        visible=True,
                        bgcolor=self.parn.DEFAULT_BG,
                        thickness=0.4  # Height of RangeSlider/thumbnail
                        # autorange=True,
                    )
                )
            )
            # Note: This `range` is different than the range argument in Figure creation, which crops off data
            fig['layout']['xaxis']['range'] = [
                self.rec.sample_count_to_time_str(self.parn.DISP_RNG_INIT[0][0]),
                self.rec.sample_count_to_time_str(self.parn.DISP_RNG_INIT[0][1])
            ]
            # fig['layout']['line']['width'] = 0.5
            return fig

        @staticmethod
        def _get_yaxis_code(i):
            return f'y{i}' if i > 0 else 'y'

        def add_trace(self, idxs_lead_add, override=False):
            if override:
                self.fig['data'] = []
            offset = len(self.idxs_lead)  # Append to axis based on existing number of leads plotted
            for idx_idx, idx_lead in enumerate(idxs_lead_add):
                y_vals = self.parn.get_y_vals(idx_lead, self.strt, self.end, self.sample_factor)
                rang = self.parn.parn.ui.get_ignore_noise_range(y_vals)
                self.fig.add_trace(go.Scatter(
                    x=self.x_vals,
                    y=self.parn.parn.ui.strip_noise(y_vals, rang[0], rang[1]),
                    yaxis=self._get_yaxis_code(idx_idx + offset)
                ))
            self.fig.update_traces(
                line=dict(width=0.5)
            )

            self.fig['layout']['xaxis']['range'] = \
                self.parn.display_range_to_layout_range(self.parn.parn.curr_disp_rng[0])
            return self.fig

    def display_range_to_layout_range(self, rang):
        strt, end = rang
        return [
            self.rec.sample_count_to_time_str(strt),
            self.rec.sample_count_to_time_str(end)
        ]

    def to_time_axis(self, sample_counts):
        """
        :return: Evenly spaced array of incremental time stamps in microseconds
        """
        if floor(self.FAC_TO_US) == self.FAC_TO_US:  # Is an int
            sample_counts *= int(self.FAC_TO_US)
        else:
            sample_counts = (sample_counts * self.FAC_TO_US).astype(np.int64)
        # Converted to time in microseconds as integer, drastically raises efficiency while maintaining precision
        return pd.to_datetime(pd.Series(sample_counts), unit='us')

    def get_sample_factor(self, strt, end):
        return max(self._get_sample_factor(strt, end), self.min_sample_step)

    def _get_sample_factor(self, strt, end):
        # If showing too a small range, sample_factor which is incremental steps should be at least 1
        return max((end - strt + 1) // (self._DISPLAY_WIDTH * self._DISPLAY_SCALE_T), 1)
