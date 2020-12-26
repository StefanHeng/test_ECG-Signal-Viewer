import numpy as np

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

    def __init__(self, parent):  # Linked record automatically updates by parent
        self.parn = parent

    def get_display_range(self, layout_fig):
        """
        :param layout_fig: Layout of Plotly graph object
        :return: 2*2 List of List containing x and y axis range
        """
        x_range = layout_fig['xaxis']['range']
        return [[
            self.parn.curr_rec.time_str_to_sample_count(x_range[0]),
            self.parn.curr_rec.time_str_to_sample_count(x_range[1])],
            layout_fig['yaxis']['range']
        ]

    def get_x_display_range(self, layout_fig):
        x_range = layout_fig['xaxis']['range']
        return [
            self.parn.curr_rec.time_str_to_sample_count(x_range[0]),
            self.parn.curr_rec.time_str_to_sample_count(x_range[1])
        ]

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
        # print(f'samples is {samples}')
        # idx_med = self.NUM_SAMPLES // 2
        # med = samples[idx_med]
        half_range = max(samples[self.PERCENT_NUM-1], samples[-self.PERCENT_NUM])  # For symmetry
        half_range *= 20  # By nature of ECG waveform signals
        return -half_range, half_range

