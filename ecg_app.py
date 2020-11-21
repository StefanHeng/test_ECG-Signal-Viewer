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
    # Keys inside `relayoutData`
    KEY_X_S = 'xaxis.range[0]'  # Start limit for horizontals axis
    KEY_X_E = 'xaxis.range[1]'
    KEY_Y_S = 'yaxis.range[0]'
    KEY_Y_E = 'yaxis.range[1]'

    DISPLAY_RANGE_INIT = [
        [0, 100000],  # 100s
        [-4000, 4000]  # -4V to 4V
    ]
    PRESERVE_UI_STATE = True  # Arbitrarily picked value
    COLOR_PLOT = '#6AA2F9'  # Default blue by plotly
    PRIMARY = '#FCA912'
    SECONDARY = '#2C8595'
    SECONDARY_2 = '#80B6BF'
    GRAY_0 = '#808080'  # Gray

    def __init__(self, app_name):
        # Ad-hoc values for now, in the future should be calculated from device info
        # Default starting point, in the future should be retrieved from user
        self._display_width = 100  # in rem, display_width * display_scale_t gets the number of points to render
        self._display_scale_t = 20  # #continuous time stamps to display in 1rem
        self._display_scale_ecg = 20  # magnitude of ecg in a 1rem
        # A valid range has values in [0, sum of all samples across the entire ecg_record)
        # Inclusive start and end
        # one-to-one correspondence with time by `sample_rate`
        self._display_range = self.DISPLAY_RANGE_INIT

        self.app_name = app_name
        self.app = dash.Dash(self.app_name)
        self.curr_recr = None  # Current record
        self.curr_recr_figs = None

    def set_curr_record(self, record_path):
        """Current record selected to display. Previous record data overridden """
        self.curr_recr = EcgRecord(record_path)
        self.curr_recr_figs = {}

    def add_plot(self, idx_lead):
        """
        Make sure a record is selected, plot on a lead dependent on record selected
        :param idx_lead:
        :return:
        """
        plot = self.EcgPlot(self.curr_recr, self)
        self.curr_recr_figs[idx_lead] = plot  # Other code need to make sure no index collision
        return plot

    def get_plot_fig(self, idx_lead):
        strt, end = self._display_range[0]
        # determine if optimization is needed for large sample_range
        sample_factor = (end - strt + 1) // (self._display_width * self._display_scale_t)
        return self.curr_recr_figs[idx_lead].get_fig(idx_lead, strt, end, sample_factor)

    def get_plot_xy_vals(self, idx_lead):
        strt, end = self._display_range[0]
        # determine if optimization is needed for large sample_range
        sample_factor = (end - strt + 1) // (self._display_width * self._display_scale_t)
        return self.curr_recr_figs[idx_lead].get_xy_vals(idx_lead, strt, end, sample_factor)

    def time_str_to_sample_count(self, time):
        """For Dash app time display returns a string representation """
        return self.curr_recr.time_str_to_sample_count(time)

    class EcgPlot:
        """Handles plotting for a particular `record`, or surgery.
        """

        def __init__(self, record, parent):
            self.recr = record
            self.parn = parent

        def get_xy_vals(self, idx_lead, strt, end, sample_factor):
            """
            :return: plotly line plot's x, y data points, based on current display range

            .. seealso:: `ecg_record.get_samples`
            """
            if sample_factor >= 10:
                sample_counts = np.linspace(strt, end, num=(end - strt + 1) // sample_factor)
                return self.to_time_axis(sample_counts), self.recr.get_samples(idx_lead, strt, end, sample_factor)
            else:
                # No need to sample, take all data
                return self.to_time_axis(np.arange(strt, end + 1)), self.recr.get_samples(idx_lead, strt, end)

        def get_fig(self, idx_lead, strt, end, sample_factor):
            # logger.info(f'sample_counts of size {sample_counts.shape[0]} -> {sample_counts}')
            # logger.info(f'ecg_vals of size {ecg_vals.shape[0]} -> {ecg_vals}')
            time_vals, ecg_vals = self.get_xy_vals(idx_lead, strt, end, sample_factor)
            axis_config = dict(
                showspikes=True,
                spikemode='toaxis',
                spikesnap='data',
                spikedash='dot',
                spikethickness=1,
                spikecolor=self.parn.PRIMARY,
                linecolor=self.parn.SECONDARY_2  # Axis color
            )
            return dict(
                data=[dict(
                    x=time_vals,
                    y=ecg_vals,
                    mode='lines',
                    marker=dict(
                        color=self.parn.COLOR_PLOT,
                        size=10),
                )],
                layout=dict(
                    uirevision=self.parn.PRESERVE_UI_STATE,
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

    def to_sample_lim(self, relayout_data, d_range):
        """
        Due to plotly graph_obj internal storage format of `relayoutData`

        :param relayout_data:  Horizontal, vertical plot limit,  as str representation of pandas timestamp
        :param d_range:
        :return: Horizontal, vertical plot limit in terms of sample count
        """
        if self.KEY_X_S in relayout_data:
            d_range[0] = [
                self.time_str_to_sample_count(relayout_data[self.KEY_X_S]),
                self.time_str_to_sample_count(relayout_data[self.KEY_X_E])
            ]
        elif self.KEY_Y_S in relayout_data:
            d_range[1] = [
                self.time_str_to_sample_count(relayout_data[self.KEY_Y_S]),
                self.time_str_to_sample_count(relayout_data[self.KEY_Y_E])
            ]
        return d_range
