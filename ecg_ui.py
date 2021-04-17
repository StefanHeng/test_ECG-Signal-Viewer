import numpy as np
import pandas as pd

import re
# from random import random
from enum import Enum
# from bisect import bisect_left

from icecream import ic

from ecg_app_defns import *
# from data_link import *

CLP_CH = Enum('CaliperChange', 'Add Remove Edit')  # Caliper change


def remove_by_indices(lst, idxs):
    """ Assumes idxs valid and reversely sorted """
    for i in idxs:
        del lst[i]


class EcgUi:
    # Keys inside `relayoutData`
    K_XS = 'xaxis.range[0]'  # Start limit for horizontals axis
    K_XE = 'xaxis.range[1]'
    K_YS = 'yaxis.range[0]'
    K_YE = 'yaxis.range[1]'

    K_XRNG = 'xaxis.range'

    K_SH = 'shape'
    K_X0 = f'{K_SH}'

    NUM_SAMPLES = 29  # Number of samples to take for randomization
    PERCENT_NUM = 5  # Number for a rough percentile sample count, based on NUM_SAMPLES
    PERCENTILE = 80  # Percentile for noise removal on automatic display range

    def __init__(self, record):  # Linked record automatically updates by parent
        self.rec = record
        self.calipers = [self.Caliper(record, i) for i in range(self.rec.n_lead)] if self.rec is not None else []
        self._ord_caliper = []  # History of caliper measurement by lead & caliper index 2-tuple, as a stack

    def set_record(self, record):
        self.rec = record
        self.calipers = [self.Caliper(record, i) for i in range(self.rec.n_lead)] if self.rec is not None else []
        # self.comments = self.comments.init(record)

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

    @staticmethod
    def get_ignore_noise_range(vals, z=5):
        # samples = []
        # n = vals.shape[0]  # vals should be a numpy array
        # for i in range(self.NUM_SAMPLES):
        #     samples.append(int(random() * (n + 1)))  # Uniform distribution, with slight inaccuracy
        # samples.sort()  # Small array size makes sorting efficient
        # half_range = max(samples[self.PERCENT_NUM - 1], samples[-self.PERCENT_NUM])  # For symmetry
        # half_range *= 40  # By nature of ECG waveform signals

        # Update: try standard deviation range
        # ic('in ignore noise')
        # ic()
        half_range = z * np.std(vals)
        m = np.mean(vals)
        # ic()
        return m-half_range, m+half_range

    def get_ignore_noise_range_(self, strt, end):  # TODO
        """ Returns an initial, pseudo range of ECG values given a set of samples

        Based on R peaks in the original record

        A multiple of percentile range, should include all non-outliers

        Should skip outliers/noise and include the majority of values

        :return: Start and end values """
        # Through randomization
        # ecg_vals = self.rec.get_ecg_samples(0, strt, end)
        # ic(strt, end, ecg_vals.shape)
        # peaks = ecg_vals[self.rec.r_peak_indices(strt, end)]
        peaks = self.rec.r_peak_vals(strt, end)
        sample = np.random.choice(peaks, size=min(peaks.size, self.NUM_SAMPLES), replace=False)  # Uniform distribution
        ic(peaks, sample)
        sample.sort()  # Small array size makes sorting efficient
        # half_range = max(sample[self.PERCENT_NUM - 1], sample[-self.PERCENT_NUM])  # For symmetry
        half_range = np.percentile(sample, self.PERCENTILE)
        half_range *= 1.4
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

    def count_pr_to_time_label(self, strt, end):
        return f'{self.rec.count_to_str(strt)} - {self.rec.count_to_str(end)}'

    def time_range_to_time_label(self, strt, end):
        """ Takes in time as strings """
        return f'{self.rec.pd_time_to_str(pd.Timestamp(strt))} - {self.rec.pd_time_to_str(pd.Timestamp(end))}'

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

    def has_measurement(self):
        return any(c.has_measurement for c in self.calipers)

    def update_caliper_annotations_shape(self, layout, idx_ld):
        """
        Given a changed layout and the corresponding lead index
        """
        update = self.calipers[idx_ld].update_caliper_annotations_shape(layout)
        if update == CLP_CH.Add:
            self._ord_caliper.append(idx_ld)
        elif update == CLP_CH.Edit and (idx_ld != self._ord_caliper[-1]):  # There must be at least 1 caliper left
            self._ord_caliper.append(idx_ld)
        elif update == CLP_CH.Remove and (idx_ld == self._ord_caliper[-1]):
            del self._ord_caliper[-1]

    def get_mru_caliper_coords(self):
        if self._ord_caliper:
            idx_lead = self._ord_caliper[-1]
            return idx_lead, self.calipers[idx_lead].get_mru_caliper_coords()

    def highlight_mru_caliper_edit(self, figs_gra, idxs_lead, idxs_ignore=[]):
        """ Highlights the most recently edited shapes, for a list of figures
        Potentially, need to ignore the leads removed by Dash callback nature """
        # ic(self._ord_caliper, idxs_lead)
        for i, f in enumerate(figs_gra):
            # ic(i, idxs_ignore, i not in idxs_ignore)
            idx_ld = idxs_lead[i]
            if idx_ld not in idxs_ignore:
                for idx, shape in enumerate(f['layout']['shapes']):
                    # ic(idxs_lead)
                    if idx_ld == self._ord_caliper[-1] and idx == self.calipers[idx_ld].mru_index():  # There's only 1
                        shape['fillcolor'] = CLR_CLPR_RECT_ACT
                    else:
                        shape['fillcolor'] = CLR_CLPR_RECT

    def clear_measurements(self):
        for c in self.calipers:
            c.clear_measurements()

    def get_caliper_annotations(self, idx_ld):
        return self.calipers[idx_ld].get_measurement_annotations()

    def update_caliper_lead_removed(self, idx_ld_rmv):
        """ When a single lead channel is removed
        Returns true if caliper measurements removed
        """
        idxs_rmv = [idx for idx, i in enumerate(self._ord_caliper) if i == idx_ld_rmv]
        # Remove all caliper measurement history associated with this lead
        remove_by_indices(self._ord_caliper, sorted(idxs_rmv, reverse=True))
        self.calipers[idx_ld_rmv].clear_measurements()  # Clear caliper measurements on the lead removed
        return idx_ld_rmv != []

    def update_caliper_annotations_time(self, strt, end, figs, idxs_lead):
        caliper_removed_lds = [self.calipers[idx].update_caliper_annotations_time(strt, end, figs[i])
                               for i, idx in enumerate(idxs_lead)]
        # ic(self._ord_caliper)
        if self._ord_caliper:
            idx_mru = self._ord_caliper[-1]
            # ic(idx_mru)
            while caliper_removed_lds[idxs_lead.index(idx_mru)]:
                if len(self.calipers[idx_mru]) == 0:  # No more caliper for most recent lead
                    del self._ord_caliper[-1]
                    # ic(self._ord_caliper)
                    if not self._ord_caliper:  # No more caliper history for all leads
                        break
                    else:
                        idx_mru = self._ord_caliper[-1]
            return True
        else:
            return False

    class Caliper:
        """ Handles caliper internal updates for a single lead,
        depending on `EcgApp` time range navigation and caliper measurement creation, removal and edit.
        """

        # MAX_CLP_RNG = pd.to_timedelta(20, unit='s')  # Maximum range intended for caliper usage
        UNIT_1MS = pd.to_timedelta(1, unit='ms')

        def __init__(self, record, idx_lead):
            self.rec = record
            self.idx_lead = idx_lead  # Each Caliper serves a particular lead, by index

            self._n_mesr = 0  # Number of caliper measurements, given by
            self._lst_shape_coords = []  # List to keep track of plotly user-drawn shapes, in that order
            self.lst_ann_mesr = []  # List of annotation pairs,
            # synchronized with the above, on the corresponding text annotation measurements
            self._ord_mesr_edit = []  # Keeps track of the order of elements modified by index
            # Most recent one on end of list

        def __len__(self):
            return self._n_mesr

        @staticmethod
        def shape_dict_to_coords(d_shape, changed=False):
            """
            :param d_shape: Plotly shape dictionary
            :param changed: Either the dictionary is an entire shape object or just the changes
            :return The 4-tuple coordinates in order (x0, x1, y0, y1),
            where x values are pandas time object and y values are floats

            Ensures x0 < x1, y0 < y1
            """
            if changed:  # Plotly on shape *change* returns a different dictionary
                x0, x1, y0, y1 = d_shape.values()
            else:
                x0, x1, y0, y1 = d_shape['x0'], d_shape['x1'], d_shape['y0'], d_shape['y1']
            x0 = pd.to_datetime(x0)
            x1 = pd.to_datetime(x1)
            y0, y1 = int(y0), int(y1)
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

            def _pd_time_to_ms(t):
                return t // self.UNIT_1MS

            x_diff = x1 - x0
            # if x_diff <= self.MAX_CLP_RNG:
            y_diff = int(y1 - y0)
            x = x0 + x_diff / 2
            y = int(y0) + y_diff / 2
            return (
                self.get_txt_annotation(x, y1, f'{_pd_time_to_ms(x_diff):,}ms'),
                self.get_txt_annotation(x0, y, f'{y_diff:,}mV', text_angle=-90)
            )
            # else:
            #     return None

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

        def _update_caliper_edit_order_after_remove(self, idxs_rmv):
            """ Update the attribute on (order of measurement edits based on index), based on indices already removed
            Indices removed should be reversely sorted """
            remove_by_indices(self._ord_mesr_edit, idxs_rmv)
            # ic(idxs_rmv, self._ord_mesr_edit)
            for idx_rmv in idxs_rmv:
                for idx_idx, idx in enumerate(self._ord_mesr_edit):
                    if idx > idx_rmv:  # Decrement by the right amount for the remaining elements
                        self._ord_mesr_edit[idx_idx] -= 1
            # Maintain that `ord_mesr_edit` must have uniquely every integer within [0, its length)

        def update_caliper_annotations_shape(self, layout_changed):
            """
            Expected to be called on every shape layout change, there will always be a change
            :param layout_changed: The layout of the figure change
            :return Caliper change enum type
            """
            if 'shapes' in layout_changed:  # Add/removal of shape
                lst_shape = layout_changed['shapes']
                l = len(lst_shape)
                if l > self._n_mesr:  # New shape added by user
                    coords = self.shape_dict_to_coords(lst_shape[-1])
                    self._lst_shape_coords.append(coords)
                    self.lst_ann_mesr.append(self.measure(*coords))
                    self._n_mesr += 1

                    self._ord_mesr_edit.append(self._n_mesr - 1)  # Index of newly created shape is the last one
                    return CLP_CH.Add
                # Linearly check membership for the removed rect
                else:  # A shape removed
                    def _get_idx_removed():  # There must be one and only 1 missing
                        for idx, shape in enumerate(lst_shape):
                            if self.shape_dict_to_coords(shape) != self._lst_shape_coords[idx]:
                                return idx
                        # lst_shape is the smaller one, if all equal, the last annotation is removed
                        return len(self._lst_shape_coords) - 1  # Don't use relative offset so that updating order works

                    # Must be that there were a single shape, and it's now removed
                    idx_rmv = _get_idx_removed()
                    del self._lst_shape_coords[idx_rmv]
                    del self.lst_ann_mesr[idx_rmv]
                    self._n_mesr -= 1

                    self._update_caliper_edit_order_after_remove([idx_rmv])
                    return CLP_CH.Remove
            else:  # Change to an existing shape
                def _get_idx_changed_shape(k):
                    """ User responsible for match success
                    """
                    return int(re.match(r'^shapes\[([0-9]+)]\.(.){2}$', k).group(1))

                # Any one of the keys suffice, e.g. {'shapes[2].x0', 'shapes[2].x1', 'shapes[2].y0', 'shapes[2].y1'}
                idx_ch = _get_idx_changed_shape(list(layout_changed.keys())[0])
                coords = self.shape_dict_to_coords(layout_changed, changed=True)
                self._lst_shape_coords[idx_ch] = coords
                self.lst_ann_mesr[idx_ch] = self.measure(*coords)

                idx_edt = self._ord_mesr_edit.index(idx_ch)  # Find the original ordering of this edited shape
                del self._ord_mesr_edit[idx_edt]
                self._ord_mesr_edit.append(idx_ch)  # Promote to recently edited
                return CLP_CH.Edit
            # ic(self._ord_mesr_edit)

        def update_caliper_annotations_time(self, strt, end, fig):
            """ Expected to be called on every display time range change, there might not be a change

            Removes user-drawn shapes out of range if any, in the `figs` argument

            # :return Updated list of text annotations within display time range if any measurement removed,
            False otherwise
            """

            def _get_measurement_indices_out_of_range(strt, end):
                """
                 Remove shapes that fall off the display in internal tracks

                :return: 2 tuple of if any measurement is removed, and the corresponding indices in sorted order
                """
                s = self.rec.count_to_pd_time(strt)
                e = self.rec.count_to_pd_time(end)
                removed = False
                idxs = []
                for idx, (x0, x1, y0, y1) in enumerate(self._lst_shape_coords):  # Reverse the list
                    if x0 >= e or x1 <= s:
                        removed = True
                        idxs.append(idx)
                return removed, idxs

            removed, idxs = _get_measurement_indices_out_of_range(strt, end)
            if removed:
                idxs.sort(reverse=True)
                self._n_mesr -= len(idxs)
                remove_by_indices(self._lst_shape_coords, idxs)
                remove_by_indices(self.lst_ann_mesr, idxs)
                # for f in figs:
                remove_by_indices(fig['layout']['shapes'], idxs)

                self._update_caliper_edit_order_after_remove(idxs)
            return removed

        def clear_measurements(self):
            self._n_mesr = 0
            self._lst_shape_coords = []
            self.lst_ann_mesr = []
            self._ord_mesr_edit = []

        def mru_index(self):
            """ Most recently edited caliper measurement, as index into the """
            return self._ord_mesr_edit[-1]

        def get_mru_caliper_coords(self):
            """
            :return: 4-tuple, (x0, x1, y0, y1) as pandas time objects and integer voltages
            if a measurement exists, None otherwise """
            if self.has_measurement():
                return self._lst_shape_coords[self._ord_mesr_edit[-1]]

        def has_measurement(self):
            return self._n_mesr > 0
