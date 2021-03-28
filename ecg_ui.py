import numpy as np
import pandas as pd
import re

from random import random

from icecream import ic

from ecg_app_defns import *


class EcgUi:
    # Keys inside `relayoutData`
    K_XS = 'xaxis.range[0]'  # Start limit for horizontals axis
    K_XE = 'xaxis.range[1]'
    K_YS = 'yaxis.range[0]'
    K_YE = 'yaxis.range[1]'

    K_XRNG = 'xaxis.range'

    K_SH = 'shape'
    K_X0 = f'{K_SH}'

    # MAX_CLP_RNG = pd.to_timedelta(20, unit='s')  # Maximum range intended for caliper usage
    UNIT_1MS = pd.to_timedelta(1, unit='ms')

    NUM_SAMPLES = 29  # Number of samples to take for randomization
    PERCENT_NUM = 5  # Number for a rough percentile sample count, based on NUM_SAMPLES

    def __init__(self, record):  # Linked record automatically updates by parent
        self.rec = record

        self._n_mesr = 0  # Number of caliper measurements, given by
        self._lst_shape_coord = []  # List to keep track of plotly user-drawn shapes, in that order
        self.lst_ann_mesr = []  # List of annotation pairs,
        # synchronized with the above, on the corresponding text annotation measurements

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
            self.rec.time_str_to_count(x_range[0]),
            self.rec.time_str_to_count(x_range[1])],
            layout_fig['yaxis']['range']
        ]

    def get_x_display_range(self, layout_fig):
        x_range = layout_fig['xaxis']['range']
        return [
            self.rec.time_str_to_count(x_range[0]),
            self.rec.time_str_to_count(x_range[1])
        ]

    def get_y_display_range(self, layout_fig):
        return [
            layout_fig[self.K_YS],
            layout_fig[self.K_YE]
        ]

    def get_x_layout_range(self, layout_fig):
        """
        .. note:: Clipped
        .. note:: In human-readable time stamp
        """
        # Clip start time from below to 0, end time from above to maximum sample count
        # str comparison suffices
        strt = max(layout_fig[self.K_XS], self.rec.TIME_STRT)
        end = min(layout_fig[self.K_XE], self.rec.TIME_END)
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
            samples.append(int(random() * (n + 1)))  # Uniform distribution, with slight inaccuracy
        samples.sort()  # Small array size makes sorting efficient
        half_range = max(samples[self.PERCENT_NUM - 1], samples[-self.PERCENT_NUM])  # For symmetry
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

    def get_tags(self, strt, end, idx_ann_clicked=-1):
        idx_strt, idx_end = self.rec.get_tag_indices(strt, end)
        anns = []
        on_top = True
        for idx in range(idx_strt, idx_end):
            typ, t_ms, _ = self.rec.tags[idx]
            x = self.rec.count_to_pd_time(self.rec.ms_to_count(t_ms))
            anns.append(self._get_tag(idx, x, typ, on_top=on_top, is_clicked=idx_ann_clicked == idx))
            on_top = not on_top
        return anns

    @staticmethod
    def _get_tag(idx, x, text, on_top=True, is_clicked=False):
        return dict(
            idx=idx,  # Not native to Plotly annotations
            x=x,
            y=0,  # Always at the x axis
            text=text,
            showarrow=True,
            arrowsize=0.5,
            arrowhead=0,
            arrowwidth=1.5,
            arrowcolor=ANTN_ARW_CLR,
            ax=0,
            ay=-10 if on_top else 10,  # The value itself is inverted
            yanchor='bottom' if on_top else 'top',
            borderpad=2,
            bgcolor=ANTN_BG_CLR_CLK if is_clicked else ANTN_BG_CLR
        )

    @staticmethod
    def shape_updated(layout):
        # Check substring; A change in shape has all 4 x0, x1, y0, y1
        return 'shapes' in layout or '.x0' in list(layout.keys())[0]

    @staticmethod
    def shape_dict_to_coords(d_shape, changed=False):
        """
        :param d_shape: Plotly shape dictionary
        :param changed: Either the dictionary is an entire shape object or just the changes
        :return The 4-tuple coordinates in order (x0, x1, y0, y1).

        Ensures x0 < x1, y0 < y1
        """
        if changed:  # Plotly on shape *change* returns a different dictionary
            x0, x1, y0, y1 = d_shape.values()
        else:
            x0, x1, y0, y1 = d_shape['x0'], d_shape['x1'], d_shape['y0'], d_shape['y1']
        x0 = pd.to_datetime(x0)
        x1 = pd.to_datetime(x1)
        x0, x1 = (x0, x1) if x0 < x1 else (x1, x0)  # The relative magnitude depends on
        y0, y1 = (y0, y1) if y0 < y1 else (y1, y0)
        return x0, x1, y0, y1

    def measure(self, x0, x1, y0, y1):
        """
        Based on mid-point coordinates.

        As design choice, the measurement shown at the left and top edge of the rectangle

        :param x0: x coordinate on left
        :param x1: x coordinate on right
        :param y0: y coordinate on bottom
        :param y1: y coordinate on top
        :return: A 2-tuple of plotly annotation-accepted dict, measurement for time and voltage axes respectively

        """
        x_diff = x1 - x0
        # if x_diff <= self.MAX_CLP_RNG:
        y_diff = int(y1 - y0)
        x = x0 + x_diff / 2
        y = int(y0) + y_diff / 2
        return (
            self.get_txt_annotation(x, y1, f'{self._pd_time_to_ms(x_diff):,}ms'),
            self.get_txt_annotation(x0, y, f'{y_diff:,}mV', text_angle=-90)
        )
        # else:
        #     return None

    def _pd_time_to_ms(self, t):
        return t // self.UNIT_1MS

    @staticmethod
    def get_txt_annotation(x, y, s, text_angle=0):  # Like `_get_tag`, both returns
        return dict(
            x=x,
            y=y,
            text=s,
            textangle=text_angle,
            borderpad=2,
            bgcolor=ANTN_BG_CLR_A5
        )

    def get_measurement_annotations(self):
        return [ann for pr in self.lst_ann_mesr for ann in pr]  # Flattens 2d list to 1d

    def update_measurement_annotations_shape(self, layout_changed):
        """
        Expected to be called on every shape layout change, there will always be a change
        :param layout_changed: The layout of the figure change
        """
        if 'shapes' in layout_changed:  # Add/removal of shape
            lst_shape = layout_changed['shapes']
            l = len(lst_shape)
            if l > self._n_mesr:  # New shape added by user
                coords = self.shape_dict_to_coords(lst_shape[-1])
                self._lst_shape_coord.append(coords)
                self.lst_ann_mesr.append(self.measure(*coords))
                self._n_mesr += 1
            # Linearly check membership for the removed rect
            else:  # A shape removed
                def _get_idx_removed():  # There must be one and only 1 missing
                    for idx, shape in enumerate(lst_shape):
                        if self.shape_dict_to_coords(shape) != self._lst_shape_coord[idx]:
                            return idx
                    return -1  # lst_shape is the smaller one, if all equal, the last annotation is removed
                # Must be that there were a single shape, and it's now removed
                idx_rmv = _get_idx_removed()
                del self._lst_shape_coord[idx_rmv]
                del self.lst_ann_mesr[idx_rmv]
                self._n_mesr -= 1
        else:  # Change to an existing shape
            # Any one of the keys suffice, e.g. {'shapes[2].x0', 'shapes[2].x1', 'shapes[2].y0', 'shapes[2].y1'}
            idx_ch = self._get_idx_changed_shape(list(layout_changed.keys())[0])
            coords = self.shape_dict_to_coords(layout_changed, changed=True)
            self._lst_shape_coord[idx_ch] = coords
            self.lst_ann_mesr[idx_ch] = self.measure(*coords)

    @staticmethod
    def _get_idx_changed_shape(k):
        """ User responsible for match success
        """
        return int(re.match(r'^shapes\[([0-9]+)]\.(.){2}$', k).group(1))

    def update_measurement_annotations_time(self, strt, end, figs):
        """ Expected to be called on every display time range change, there might not be a change

        Removes user-drawn shapes out of range if any, in the `figs` argument

        # :return Updated list of text annotations within display time range if any measurement removed, False otherwise
        """
        removed, idxs = self._get_measurement_indices_out_of_range(strt, end)
        if removed:
            idxs.sort(reverse=True)
            self._n_mesr -= len(idxs)
            self._remove_by_indices(self._lst_shape_coord, idxs)
            self._remove_by_indices(self.lst_ann_mesr, idxs)
            for f in figs:
                self._remove_by_indices(f['layout']['shapes'], idxs)
        return removed
        #     return self.get_measurement_annotations()
        # else:
        #     return False

    def _get_measurement_indices_out_of_range(self, strt, end):
        """
         Remove shapes that fall off the display in internal tracks

        :return: 2 tuple of if any measurement is removed, and the corresponding indices in sorted order
        """
        strt = self.rec.count_to_pd_time(strt)
        end = self.rec.count_to_pd_time(end)
        removed = False
        idxs = []
        for idx, (x0, x1, y0, y1) in enumerate(self._lst_shape_coord):  # Reverse the list
            if x0 >= end or x1 <= strt:
                removed = True
                idxs.append(idx)
        return removed, idxs

    @staticmethod
    def _remove_by_indices(lst, idxs):
        """ Assumes idxs valid and reversely sorted """
        for i in idxs:
            del lst[i]

    def clear_measurements(self):
        self._n_mesr = 0
        self._lst_shape_coord = []
        self.lst_ann_mesr = []
