from ecg_record import *

import numpy as np
import pandas as pd
from math import floor

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('dev')


class EcgApp:
    """Handles the Dash web app, interface with potentially multiple records

    Encapsulates all UI interactions including HTML layout, `callbacks
    """

    DISPLAY_RANGE_INIT = [
        [0, 100000],  # 100s
        [-4000, 4000]  # -4V to 4V
    ]

    def __init__(self, app_name):
        self.app_name = app_name
        self.app = dash.Dash(self.app_name)
        self.ui = self._Ui(self)

        self.curr_recr = None  # Current record
        self.curr_plot = None
        self.curr_figs = None

        # A valid range has values in [0, sum of all samples across the entire ecg_record)
        # Inclusive start and end
        # one-to-one correspondence with time by `sample_rate`
        self._display_range = self.DISPLAY_RANGE_INIT

    def set_curr_record(self, record_path):
        """Current record selected to display. Previous record data overridden """
        self.curr_recr = EcgRecord(record_path)
        self.curr_plot = self._Plot(self.curr_recr, self)  # A `plot` servers a record
        self.curr_figs = {}

    def get_lead_fig(self, idx_lead):
        strt, end = self._display_range[0]
        # determine if optimization is needed for large sample_range
        self.curr_figs[idx_lead] = self.curr_plot.get_fig(idx_lead, strt, end)
        return self.curr_figs[idx_lead]

    def get_lead_xy_vals(self, idx_lead):
        strt, end = self._display_range[0]
        # determine if optimization is needed for large sample_range
        return self.curr_plot.get_xy_vals(idx_lead, strt, end)

    class _Plot:
        """Handles plotting for a particular `record`, or surgery.
        """

        # Ad-hoc values for now, in the future should be calculated from device info
        # Default starting point, in the future should be retrieved from user
        _DISPLAY_WIDTH = 100  # in rem, display_width * display_scale_t gets the number of points to render
        _DISPLAY_SCALE_T = 20  # #continuous time stamps to display in 1rem
        _DISPLAY_SCALE_ECG = 20  # magnitude of ecg in a 1rem

        PRESERVE_UI_STATE = True  # Arbitrarily picked value
        COLOR_PLOT = '#6AA2F9'  # Default blue by plotly
        PRIMARY = '#FCA912'
        SECONDARY = '#2C8595'
        SECONDARY_2 = '#80B6BF'
        GRAY_0 = '#808080'  # Gray

        def __init__(self, record, parent):
            self.recr = record
            self.parn = parent

        def get_xy_vals(self, idx_lead, strt, end):
            """
            :return: plotly line plot's x, y data points, based on current display range

            .. seealso:: `ecg_record.get_samples`
            """
            sample_factor = self._get_sample_factor(strt, end)
            if sample_factor >= 10:
                sample_counts = np.linspace(strt, end, num=(end - strt + 1) // sample_factor)
                return self.to_time_axis(sample_counts), self.recr.get_samples(idx_lead, strt, end, sample_factor)
            else:
                # No need to sample, take all data
                return self.to_time_axis(np.arange(strt, end + 1)), self.recr.get_samples(idx_lead, strt, end)

        def get_fig(self, idx_lead, strt, end):
            # logger.info(f'sample_counts of size {sample_counts.shape[0]} -> {sample_counts}')
            # logger.info(f'ecg_vals of size {ecg_vals.shape[0]} -> {ecg_vals}')
            time_vals, ecg_vals = self.get_xy_vals(idx_lead, strt, end)
            axis_config = dict(
                showspikes=True,
                spikemode='toaxis',
                spikesnap='data',
                spikedash='dot',
                spikethickness=1,
                spikecolor=self.PRIMARY,
                linecolor=self.SECONDARY_2  # Axis color
            )
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
                    xaxis=axis_config,
                    yaxis=axis_config
                )
            )

        def to_time_axis(self, sample_counts):
            """
            :return: Evenly spaced array of incremental time stamps in microseconds
            """
            factor = 10 ** 6 / self.recr.sample_rate
            if floor(factor) == factor:  # Is an int
                sample_counts *= int(factor)
            else:
                sample_counts = (sample_counts * factor).astype(np.int64)
            # Converted to time in microseconds as integer, drastically raises efficiency while maintaining precision
            return pd.to_datetime(pd.Series(sample_counts), unit='us')

        def _get_sample_factor(self, strt, end):
            return (end - strt + 1) // (self._DISPLAY_WIDTH * self._DISPLAY_SCALE_T)

    class _Ui:
        # Keys inside `relayoutData`
        KEY_X_S = 'xaxis.range[0]'  # Start limit for horizontals axis
        KEY_X_E = 'xaxis.range[1]'
        KEY_Y_S = 'yaxis.range[0]'
        KEY_Y_E = 'yaxis.range[1]'

        def __init__(self, parent):
            self.parn = parent

        def to_sample_lim(self, relayout_data, d_range):
            """
            Due to plotly graph_obj internal storage format of `relayoutData`

            :param relayout_data:  Horizontal, vertical plot limit,  as str representation of pandas timestamp
            :param d_range: Previous sample count range
            :return: Horizontal, vertical plot limit in terms of sample count
            """
            if self.KEY_X_S in relayout_data:
                d_range[0] = [
                    self.parn.curr_recr.time_str_to_sample_count(relayout_data[self.KEY_X_S]),
                    self.parn.curr_recr.time_str_to_sample_count(relayout_data[self.KEY_X_E])
                ]
            elif self.KEY_Y_S in relayout_data:
                d_range[1] = [
                    self.parn.curr_recr.time_str_to_sample_count(relayout_data[self.KEY_Y_S]),
                    self.parn.curr_recr.time_str_to_sample_count(relayout_data[self.KEY_Y_E])
                ]
            return d_range

