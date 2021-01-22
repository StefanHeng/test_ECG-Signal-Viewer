import numpy as np
import re

from random import random


class EcgUi:
    # Keys inside `relayoutData`
    KEY_X_S = 'xaxis.range[0]'  # Start limit for horizontals axis
    KEY_X_E = 'xaxis.range[1]'
    KEY_Y_S = 'yaxis.range[0]'
    KEY_Y_E = 'yaxis.range[1]'

    KEY_X_RNG = 'xaxis.range'

    NUM_SAMPLES = 29  # Number of samples to take for randomization
    PERCENT_NUM = 5  # Number for a rough percentile sample count, based on NUM_SAMPLES

    def __init__(self, record):  # Linked record automatically updates by parent
        self.rec = record

    def set_record(self, record):
        self.rec = record

    def get_display_range(self, layout_fig):
        """
        :param layout_fig: Layout of Plotly graph object
        :return: 2*2 List of List containing x and y axis range

        .. note:: By sample count
        """
        x_range = layout_fig['xaxis']['range']
        return [[
            self.rec.time_str_to_sample_count(x_range[0]),
            self.rec.time_str_to_sample_count(x_range[1])],
            layout_fig['yaxis']['range']
        ]

    def get_x_display_range(self, layout_fig):
        x_range = layout_fig['xaxis']['range']
        return [
            self.rec.time_str_to_sample_count(x_range[0]),
            self.rec.time_str_to_sample_count(x_range[1])
        ]

    def get_y_display_range(self, layout_fig):
        return [
            layout_fig[self.KEY_Y_S],
            layout_fig[self.KEY_Y_E]
        ]

    def get_x_layout_range(self, layout_fig):
        """
        .. note:: Clipped
        .. note:: In human-readable time stamp
        """
        # Clip start time from below to 0, end time from above to maximum sample count
        # str comparison suffices
        strt = max(layout_fig[self.KEY_X_S], self.rec.TIME_STRT)
        end = min(layout_fig[self.KEY_X_E], self.rec.TIME_END)
        return [strt, end]

    @staticmethod
    def strip_noise(vals, bot, top):
        """ For thumbnail range, gives accurate range given by setting outliers to 0
        """
        return np.vectorize(lambda x: x if bot < x < top else 0)(vals)

    def get_ignore_noise_range(self, vals):  # TODO
        """ Returns an initial, pseudo range of ECG values given a set of samples

        A multiple of percentile range, should include all non-outliers

        Should skip outliers/noise and include the majority of values

        :return: Start and end values """
        # Through randomization
        samples = []
        n = vals.shape[0]  # vals should be a numpy array
        for i in range(self.NUM_SAMPLES):
            samples.append(int(random() * (n+1)))  # Uniform distribution, with slight inaccuracy
        samples.sort()  # Small array size makes sorting efficient
        half_range = max(samples[self.PERCENT_NUM-1], samples[-self.PERCENT_NUM])  # For symmetry
        half_range *= 40  # By nature of ECG waveform signals
        return -half_range, half_range

    @staticmethod
    def get_pattern_match_index(str_id):
        """ Per pattern-matching index construction by Dash """
        # e.g. 1 in `{"index":1,"type":"graph"}.relayoutData`
        return int(re.match("^{\"index\":([0-9]+)", str_id).group(1))

    @staticmethod
    def get_id(str_id):
        """ Get the dash element id, out of `id.property` format """
        # For checking id equality is more efficient compared to checking substring
        if str_id[0] == '{':  # Pattern-match ID
            return re.match("^{\"index\":[0-9]+,\"type\":\"(.*)\"}[.](.*)$", str_id).group(1)
        else:
            return re.match("^(.*)[.](.*)$", str_id).group(1)


