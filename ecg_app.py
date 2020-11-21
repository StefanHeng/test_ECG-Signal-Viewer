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

PRESERVE_UI_STATE = 'keep'

class EcgApp:
    """Handles the Dash web app, interface with potentially multiple records
    """
    DISPLAY_RANGE_INIT = [
        [0, 100000],  # 100s
        [-4000, 4000]  # -4V to 4V
    ]

    def __init__(self, app_name):
        # Ad-hoc values for now, in the future should be calculated from device info
        # Default starting point, in the future should be retrieved from user
        self._display_width = 100  # in rem, display_width * display_scale_t gets the number of points to render
        self._display_scale_t = 20  # #continuous time stamps to display in 1rem
        self._display_scale_ecg = 20  # magnitude of ecg in a 1rem
        # A valid range has values [0, sum of all samples across the entire ecg_record)
        # Inclusive start and end
        # self._display_range = (1, 200000)  # based on #samples, one-to-one correspondence with time by `sample_rate`
        self._display_range = self.DISPLAY_RANGE_INIT

        self.app_name = app_name
        self.app = dash.Dash(self.app_name)
        self.curr_recd = None
        self.curr_recd_figs = None

    def set_curr_record(self, record_path):
        """Current record selected to display. Previous record data overridden """
        self.curr_recd = EcgRecord(record_path)
        self.curr_recd_figs = {}

    def add_plot(self, idx_lead):
        """
        Make sure a record is selected, plot on a lead dependent on record selected
        :param idx_lead:
        :return:
        """
        plot = self.EcgPlot(self.curr_recd)
        self.curr_recd_figs[idx_lead] = plot  # Make sure no index collision
        return plot

    def get_plot_fig(self, idx_lead):
        strt, end = self._display_range[0]
        # determine if optimization is needed for large sample_range
        sample_factor = (end - strt + 1) // (self._display_width * self._display_scale_t)
        return self.curr_recd_figs[idx_lead].get_fig(idx_lead, strt, end, sample_factor)

    def get_plot_xy_vals(self, idx_lead):
        strt, end = self._display_range[0]
        # determine if optimization is needed for large sample_range
        sample_factor = (end - strt + 1) // (self._display_width * self._display_scale_t)
        return self.curr_recd_figs[idx_lead].get_xy_vals(idx_lead, strt, end, sample_factor)

    def time_str_to_sample_count(self, time):
        """For Dash app time display returns a string representation """
        return self.curr_recd.time_str_to_sample_count(time)

    class EcgPlot:
        """Handles plotting for a single `record`, or surgery.
        """

        def __init__(self, record):
            self.record = record

        def get_xy_vals(self, idx_lead, strt, end, sample_factor):
            if sample_factor >= 10:
                sample_counts = np.linspace(strt, end, num=(end - strt + 1) // sample_factor)
                return self.get_time_axis(sample_counts), \
                       self.record.get_samples(idx_lead, strt, end, sample_factor)
            else:
                # No need to take steps for small sample_factor
                return self.get_time_axis(np.arange(strt, end + 1)), \
                       self.record.get_samples(idx_lead, strt, end)

        def get_fig(self, idx_lead, strt, end, sample_factor):
            """
            :param idx_lead: index of lead
            :return: plotly line plot based on current display range

            .. seealso:: `ecg_record.get_samples`
            """
            # logger.info(f'sample_counts of size {sample_counts.shape[0]} -> {sample_counts}')
            # logger.info(f'ecg_vals of size {ecg_vals.shape[0]} -> {ecg_vals}')
            time_vals, ecg_vals = self.get_xy_vals(idx_lead, strt, end, sample_factor)
            # fig = go.Figure(
            #     data=go.Scatter(
            #         x=time_vals,
            #         y=ecg_vals
            #     )
            # )
            # fig.update_layout(
            #     title=f'Lead with index [{idx_lead}]',
            #     # xaxis_title="time(s)",
            #     # yaxis_title="ECG Signal Magnitude(mV)",
            #     dragmode='pan',
            #     # margin=dict(l=0, r=0, t=50, b=0),
            #     # margin={'l': 0, 'r': 0, 't': 50, 'b': 0}
            # )
            # return fig
            data = [{
                'x': time_vals,
                'y': ecg_vals,
                'mode': 'lines'
            }]
            return {
                'data': data,
                'layout': {
                    'uirevision': PRESERVE_UI_STATE,
                    'dragmode': 'pan',
                    'margin': {'l': 40, 'r': 0, 't': 0, 'b': 15},
                    'hoverdistance': 0,
                    'hoverinfo': None,
                    'xaxis': {
                        'showspikes': True,
                        'spikemode': 'toaxis',
                        'spikesnap': 'data',
                        'spikedash': 'dot',
                        'spikethickness': 0.125,
                        'spikecolor': '#ff0000'
                    },
                    'yaxis': {
                        'showspikes': True,
                        'spikemode': 'toaxis',
                        'spikesnap': 'data',
                        'spikedash': 'dot',
                        'spikethickness': 0.125,
                        'spikecolor': '#ff0000'
                    }
                },
                # fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False,
                #                  showspikes=True, spikemode='across', spikesnap='cursor', showline=False,
                #                  spikedash='solid')
            }

        def get_time_axis(self, arr):
            """
            :return: Evenly spaced 1D array of incremental time stamps in microseconds
            """
            factor = 10 ** 6 / self.record.sample_rate
            if floor(factor) == factor:  # Is an int
                arr *= int(factor)
            else:
                arr = (arr * factor).astype(np.int64)
            # Converted to time in microseconds as integer, drastically raises efficiency while maintaining precision
            return pd.to_datetime(pd.Series(arr), unit='us')

        # @staticmethod
        # def example(idx_lead=0):
        #     import pathlib
        #     ecg_plot = EcgApp.EcgPlot(DATA_PATH.joinpath(selected_record))
        #     return ecg_plot.get_plot(idx_lead)

    def parse_plot_lim(self, relayout_data, d_range):
        if 'xaxis.range[0]' in relayout_data:
            d_range[0] = [
                self.time_str_to_sample_count(relayout_data['xaxis.range[0]']),
                self.time_str_to_sample_count(relayout_data['xaxis.range[1]'])
            ]
        elif 'yaxis.range[0]' in relayout_data:
            d_range[1] = [
                self.time_str_to_sample_count(relayout_data['yaxis.range[0]']),
                self.time_str_to_sample_count(relayout_data['yaxis.range[1]'])
            ]
        return d_range

