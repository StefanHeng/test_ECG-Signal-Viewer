import numpy as np

import re
from typing import List

from icecream import ic

from ecg_defns_n_util import *


def _shape_dict_to_coords(d_shape, changed=False):
    """
    :param d_shape: Plotly shape dictionary
    :param changed: Either the dictionary is an entire shape object or just the changes
    :return The 4-tuple coordinates in order (x0, x1, y0, y1),
    where x values are pandas time object and y values are integers

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


def _get_idx_removed(lst_shape, lst_coords):  # There must be one and only 1 missing
    for idx, shape in enumerate(lst_shape):
        if _shape_dict_to_coords(shape) != lst_coords[idx]:
            return idx
    # lst_shape is the smaller one, if all equal, the last annotation is removed
    return len(lst_coords) - 1  # Don't use relative offset so that updating order works


def _get_txt_annotation(x, y, s, text_angle=0):  # Like `_get_tag`, both returns plotly annotations
    return dict(
        x=x,
        y=y,
        text=s,
        textangle=text_angle,
        borderpad=2,
        bgcolor=ANTN_BG_CLR_A5
    )


def _measure(x0, x1, y0, y1):
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
    y_diff = int(y1 - y0)
    x = x0 + x_diff / 2
    y = int(y0) + y_diff / 2
    return (
        _get_txt_annotation(x, y1, f'{pd_time_to_ms(x_diff):,}ms'),
        _get_txt_annotation(x0, y, f'{y_diff:,}mV', text_angle=-90)
    )


def _get_caliper_indices_out_of_range(lst_coords, strt, end):
    """
     Remove shapes that fall off the display in internal tracks

    :return: 2 tuple of if any measurement is removed, and the corresponding indices in sorted order
    """
    removed = False
    idxs = []
    for idx, (x0, x1, y0, y1) in enumerate(lst_coords):  # Reverse the list
        if x0 >= end or x1 <= strt:
            removed = True
            idxs.append(idx)
    return removed, idxs


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
        # Starts with independent calipers
        self.clp = self.CaliperI(record)
        self.sync = CLP_SYNC.Independent

    def set_record(self, record):
        self.rec = record
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
        half_range = z * np.std(vals)
        m = np.mean(vals)
        return m - half_range, m + half_range

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

    def toggle_caliper_synchronization(self):
        self.clear_measurements()  # TODO: For now
        if self.sync == CLP_SYNC.Independent:
            self.sync = CLP_SYNC.Synchronized
            self.caliper_independent_to_synchronized()
        else:
            self.sync = CLP_SYNC.Independent
            self.caliper_synchronized_to_independent()

    def caliper_is_synchronized(self):
        return self.sync == CLP_SYNC.Synchronized

    def caliper_independent_to_synchronized(self):
        """ Renders the figures as necessary """
        self.clp: EcgUi.CaliperI
        c = self.CaliperS(self.clp.rec)  # For now, caliper is CaliperI instance
        # TODO
        # if self.clp.has_measurement():
        #     c.from_independent(*self.clp.to_synchronized())
        # ic(ord_caliper, ld_idxs_coord, lst_coords)
        self.clp = c
        # self.clp.render(figs)

    def caliper_synchronized_to_independent(self):
        c = self.CaliperI(self.clp.rec)
        self.clp = c

    def get_caliper_annotations(self, idx_ld):
        if self.sync == CLP_SYNC.Independent:
            return self.clp.get_caliper_annotations(idx_ld)
        else:
            self.clp: EcgUi.CaliperS
            return self.clp.get_caliper_annotations()

    def clear_measurements(self):
        self.clp.clear_measurements()

    def update_caliper_annotations_shape(self, layout, idx_ld):
        """ Returns whether the caliper change was caliper creation/edit/removal """
        return self.clp.update_caliper_annotations_shape(layout, idx_ld)

    def highlight_mru_caliper_edit(self, figs_gra, idxs_lead=[], idxs_ignore=[]):
        if self.caliper_is_synchronized():
            self.clp: EcgUi.CaliperS
            self.clp.highlight_mru_caliper_edit(figs_gra)
        else:
            self.clp.highlight_mru_caliper_edit(figs_gra, idxs_lead, idxs_ignore)

    def has_measurement(self):
        return self.clp.has_measurement()

    def get_mru_caliper_coords(self):
        return self.clp.get_mru_caliper_coords()

    def update_caliper_annotations_time(self, strt, end, figs, idxs_lead, idx_ld_ch):
        if self.caliper_is_synchronized():
            return self.clp.update_caliper_annotations_time(strt, end, figs, idx_ld_ch)
        else:
            return self.clp.update_caliper_annotations_time(strt, end, figs, idxs_lead)

    def update_caliper_lead_removed(self, idx_ld_rmv):
        if not self.caliper_is_synchronized():  # Independent calipers
            self.clp.update_caliper_lead_removed(idx_ld_rmv)

    def caliper_on_display(self, idx_ld, xc, yc, x0, y0):
        """ Checks if a potential comment has its corresponding caliper already loaded """
        return self.clp.caliper_on_display(idx_ld, xc, yc, x0, y0)

    def load_caliper_by_cmt(self, figs_gra, xc, yc, x0, y0, idx_idx_ld):
        shape = dict(
            type='rect',
            x0=str(self.rec.count_to_pd_time(x0)),
            x1=str(self.rec.count_to_pd_time(x0 + 2 * (xc - x0))),
            y0=y0,
            y1=y0 + 2 * (yc - y0)
        )
        shape = merge_d(shape, TPL_SHAPE)
        if self.caliper_is_synchronized():
            for f in figs_gra:
                f['layout']['shapes'].append(shape)
        else:
            figs_gra[idx_idx_ld]['layout']['shapes'].append(shape)

    class CaliperI:
        """ Independent caliper for each lead """

        def __init__(self, record):
            self.rec = record
            self.calipers = [self.Caliper(record, i) for i in range(self.rec.n_lead)] if self.rec is not None else []
            self._ord_caliper = []  # History of caliper measurement by lead index as a stack,
            # shared across synchronized & independent calipers

            self._idx_ld_last = None

        def to_synchronized(self) -> (List[int], List[int], List, List):
            """ Transfer information for switching to synchronized calipers """
            # ic(flatten(*[c.to_synchronized() for c in self.calipers]))
            ld_idxs_coord, lst_coords = list(zip(*flatten(*[c.to_synchronized() for c in self.calipers])))
            lst_ann_mesr = flatten(*[c.lst_ann_mesr for c in self.calipers])
            return self._ord_caliper, list(ld_idxs_coord), list(lst_coords), lst_ann_mesr

        def has_measurement(self):
            return any(c.has_measurement for c in self.calipers)

        def update_caliper_annotations_shape(self, layout, idx_ld):
            """
            Given a changed layout and the corresponding lead index
            """
            update, edited_prev = self.calipers[idx_ld].update_caliper_annotations_shape(layout)
            if self._idx_ld_last != idx_ld:
                edited_prev = False
                self._idx_ld_last = idx_ld
            if update == CLP_CH.Add:
                self._ord_caliper.append(idx_ld)
            elif update == CLP_CH.Edit and (idx_ld != self._ord_caliper[-1]):  # There must be at least 1 caliper left
                self._ord_caliper.append(idx_ld)
            elif update == CLP_CH.Remove and (idx_ld == self._ord_caliper[-1]):
                del self._ord_caliper[-1]
            return update, edited_prev

        def get_mru_caliper_coords(self):
            if self._ord_caliper:
                idx_lead = self._ord_caliper[-1]
                return idx_lead, self.calipers[idx_lead].get_mru_caliper_coords()

        def highlight_mru_caliper_edit(self, figs_gra, idxs_lead, idxs_ignore=[]):
            """ Highlights the most recently edited shapes, for a list of figures
            Potentially, need to ignore the leads removed by Dash callback nature """
            for i, f in enumerate(figs_gra):
                idx_ld = idxs_lead[i]
                if idx_ld not in idxs_ignore:
                    for idx, shape in enumerate(f['layout']['shapes']):
                        # There's only 1
                        if idx_ld == self._ord_caliper[-1] and idx == self.calipers[idx_ld].mru_index():
                            shape['fillcolor'] = CLR_CLPR_RECT_ACT
                        else:
                            shape['fillcolor'] = CLR_CLPR_RECT

        def clear_measurements(self):
            self._ord_caliper = []
            for c in self.calipers:
                c.clear_measurements()

        def get_caliper_annotations(self, idx_ld):
            return self.calipers[idx_ld].get_caliper_annotations()

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
            caliper_removed_lds, edited_prevs = map(list, zip(
                *[self.calipers[idx].update_caliper_annotations_time(strt, end, figs[i])
                  for i, idx in enumerate(idxs_lead)]))
            edited_prev = True
            if self._ord_caliper:
                idx_mru = self._ord_caliper[-1]
                if not edited_prevs[idxs_lead.index(idx_mru)]:
                    edited_prev = False
                while caliper_removed_lds[idxs_lead.index(idx_mru)]:
                    if len(self.calipers[idx_mru]) == 0:  # No more caliper for most recent lead
                        del self._ord_caliper[-1]
                        if not self._ord_caliper:  # No more caliper history for all leads
                            break
                        else:
                            idx_mru = self._ord_caliper[-1]
                return True, edited_prev
            else:
                return False, edited_prev

        def caliper_on_display(self, idx_ld, xc, yc, x0, y0):
            return self.calipers[idx_ld].caliper_on_display(xc, yc, x0, y0)

        class Caliper:
            """ Handles caliper internal updates for a single lead,
            depending on `EcgApp` time range navigation and caliper measurement creation, removal and edit.
            """

            # MAX_CLP_RNG = pd.to_timedelta(20, unit='s')  # Maximum range intended for caliper usage

            def __init__(self, record, idx_lead):
                self.rec = record
                self.idx_lead = idx_lead  # Each Caliper serves a particular lead, by index

                self._n_mesr = 0  # Number of caliper measurements, given by
                self.lst_coords = []  # List to keep track of plotly user-drawn shapes, in that order
                self.lst_ann_mesr = []  # List of annotation pairs,
                # synchronized with the above, on the corresponding text annotation measurements
                self._ord_mesr_edit = []  # Keeps track of the order of elements modified by index
                # Most recent one on end of list

                self._idx_shape_last = None  # Index of caliper last edit, per Dash `shapes` list storage order

            def __len__(self):
                return self._n_mesr

            def to_synchronized(self):
                # Each caliper coordinates with the associated lead index
                return list(zip([self.idx_lead] * self._n_mesr, self.lst_coords))

            def get_caliper_annotations(self):
                return flatten(*self.lst_ann_mesr)
                # return [ann for pr in self.lst_ann_mesr for ann in pr]  # Flattens 2d list to 1d

            def _update_caliper_edit_order_after_remove(self, idxs_rmv):
                """ Update the attribute on (order of measurement edits based on index),
                based on indices already removed
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
                :return Caliper change enum type, and whether edited the same caliper as last edit
                """
                if 'shapes' in layout_changed:  # Add/removal of shape
                    lst_shape = layout_changed['shapes']
                    l = len(lst_shape)
                    if l > self._n_mesr:  # New shape added by user
                        coords = _shape_dict_to_coords(lst_shape[-1])
                        self.lst_coords.append(coords)
                        self.lst_ann_mesr.append(_measure(*coords))

                        self._ord_mesr_edit.append(self._n_mesr)  # Index of newly created shape is always the last one
                        self._idx_shape_last = self._n_mesr
                        self._n_mesr += 1
                        return CLP_CH.Add, False
                    # Linearly check membership for the removed rect
                    else:  # A shape removed
                        # Must be that there were a single shape, and it's now removed
                        idx_rmv = _get_idx_removed(lst_shape, self.lst_coords)
                        del self.lst_coords[idx_rmv]
                        del self.lst_ann_mesr[idx_rmv]
                        self._n_mesr -= 1
                        self._idx_shape_last = None

                        self._update_caliper_edit_order_after_remove([idx_rmv])
                        return CLP_CH.Remove, False
                else:  # Change to an existing shape
                    def _get_idx_changed_shape(k):
                        """ User responsible for match success
                        """
                        return int(re.match(r'^shapes\[([0-9]+)]\.(.){2}$', k).group(1))

                    # Any one of the keys suffice, e.g. {'shapes[2].x0', 'shapes[2].x1', 'shapes[2].y0', 'shapes[2].y1'}
                    idx_ch = _get_idx_changed_shape(list(layout_changed.keys())[0])
                    if idx_ch == self._idx_shape_last:
                        edited_prev = True
                    else:
                        edited_prev = False
                        self._idx_shape_last = idx_ch
                    coords = _shape_dict_to_coords(layout_changed, changed=True)
                    self.lst_coords[idx_ch] = coords
                    self.lst_ann_mesr[idx_ch] = _measure(*coords)

                    idx_edt = self._ord_mesr_edit.index(idx_ch)  # Find the original ordering of this edited shape
                    del self._ord_mesr_edit[idx_edt]
                    self._ord_mesr_edit.append(idx_ch)  # Promote to recently edited
                    return CLP_CH.Edit, edited_prev

            def update_caliper_annotations_time(self, strt, end, fig):
                """ Expected to be called on every display time range change, there might not be a change

                Removes user-drawn shapes out of range if any, in the `figs` argument

                # :return Updated list of text annotations within display time range if any measurement removed,
                False otherwise
                """
                removed, idxs = _get_caliper_indices_out_of_range(
                    self.lst_coords,
                    self.rec.count_to_pd_time(strt),
                    self.rec.count_to_pd_time(end)
                )
                if self._idx_shape_last in idxs:
                    edited_prev = False
                    self._idx_shape_last = None  # Caliper removed, reset
                else:
                    edited_prev = True
                    if self._idx_shape_last is not None:
                        self._idx_shape_last -= sum(i < self._idx_shape_last for i in idxs)
                if removed:
                    idxs.sort(reverse=True)
                    self._n_mesr -= len(idxs)
                    remove_by_indices(self.lst_coords, idxs)
                    remove_by_indices(self.lst_ann_mesr, idxs)
                    remove_by_indices(fig['layout']['shapes'], idxs)

                    self._update_caliper_edit_order_after_remove(idxs)
                return removed, edited_prev

            def clear_measurements(self):
                self._n_mesr = 0
                self.lst_coords = []
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
                    return self.lst_coords[self._ord_mesr_edit[-1]]

            def has_measurement(self):
                return self._n_mesr > 0

            def caliper_on_display(self, xc, yc, x0, y0):
                for coords in self.lst_coords:
                    if coords == (xc, yc, x0, y0):
                        return True
                return False

    class CaliperS:
        """ Synchronized caliper across all leads """

        def __init__(self, record):  # Linked record automatically updates by parent
            self.rec = record

            self._n_mesr = 0
            self.lst_coords = []
            self._ld_idxs_coord = []  # Associate each caliper measurement to it's MRU edit by lead index
            self.lst_ann_mesr = []
            self._ord_mesr_edit = []

            self._idx_shape_last = None
            self._idx_ld_last = None

        # TODO: See `ecg_app`
        # def from_independent(self, ord_caliper, ld_idxs_coord, lst_coords, lst_ann_mesr):
        #     ic(ord_caliper, ld_idxs_coord, lst_coords, lst_ann_mesr)
        #     self._n_mesr = len(self.lst_coords)
        #     self._ord_mesr_edit = ord_caliper
        #     self._ld_idxs_coord = ld_idxs_coord
        #     self.lst_coords = lst_coords
        #     self.lst_ann_mesr = lst_ann_mesr
        #
        # def render(self, figs_gra):
        #     """ Broadcast the shapes to every single channel """
        #     ic([f['layout']['shapes'] for f in figs_gra])
        #     shapes = flatten(*[f['layout']['shapes'] for f in figs_gra])
        #     ic(shapes)
        #     for f in figs_gra:
        #         f['layout']['shapes'] = shapes

        def get_caliper_annotations(self):
            return flatten(*self.lst_ann_mesr)

        def _update_measurement_edit_order_after_remove(self, idxs_rmv):
            """ Update the attribute on (order of measurement edits based on index), based on indices already removed
            Indices removed should be reversely sorted """
            remove_by_indices(self._ord_mesr_edit, idxs_rmv)
            for idx_rmv in idxs_rmv:
                for idx_idx, idx in enumerate(self._ord_mesr_edit):
                    if idx > idx_rmv:  # Decrement by the right amount for the remaining elements
                        self._ord_mesr_edit[idx_idx] -= 1
            # Maintain that `ord_mesr_edit` must have uniquely every integer within [0, its length)

        def update_caliper_annotations_shape(self, layout_changed, idx_ld):
            """
            Expected to be called on every shape layout change, there will always be a change
            :param layout_changed: The layout of the figure change
            :param idx_ld: The lead index that the shape edit is based on
            """
            if 'shapes' in layout_changed:  # Add/removal of shape
                lst_shape = layout_changed['shapes']
                l = len(lst_shape)
                if l > self._n_mesr:  # New shape added by user
                    coords = _shape_dict_to_coords(lst_shape[-1])
                    self.lst_coords.append(coords)
                    self._ld_idxs_coord.append(idx_ld)
                    self.lst_ann_mesr.append(_measure(*coords))

                    self._idx_shape_last = self._n_mesr
                    self._idx_ld_last = idx_ld
                    self._ord_mesr_edit.append(self._n_mesr)
                    self._n_mesr += 1
                    return CLP_CH.Add, False
                # Linearly check membership for the removed rect
                else:  # A shape removed
                    # Must be that there were a single shape, and it's now removed
                    idx_rmv = _get_idx_removed(lst_shape, self.lst_coords)
                    del self.lst_coords[idx_rmv]
                    del self.lst_ann_mesr[idx_rmv]
                    del self._ld_idxs_coord[idx_rmv]
                    self._n_mesr -= 1
                    self._idx_shape_last = None
                    self._idx_ld_last = None
                    if idx_ld is not None and self.has_measurement():
                        self._ld_idxs_coord[-1] = idx_ld

                    self._update_measurement_edit_order_after_remove([idx_rmv])
                    return CLP_CH.Remove, False
            else:  # Change to an existing shape
                # Any one of the keys suffice, e.g. {'shapes[2].x0', 'shapes[2].x1', 'shapes[2].y0', 'shapes[2].y1'}
                idx_ch = self._get_idx_changed_shape(list(layout_changed.keys())[0])
                coords = _shape_dict_to_coords(layout_changed, changed=True)
                self.lst_coords[idx_ch] = coords
                self.lst_ann_mesr[idx_ch] = _measure(*coords)
                self._ld_idxs_coord[idx_ch] = idx_ld

                if idx_ch == self._idx_shape_last and idx_ld == self._idx_ld_last:
                    edited_prev = True
                else:
                    edited_prev = False
                    self._idx_shape_last = idx_ch
                    self._idx_ld_last = idx_ld
                idx_edt = self._ord_mesr_edit.index(idx_ch)  # Find the original ordering of this edited shape
                del self._ord_mesr_edit[idx_edt]
                self._ord_mesr_edit.append(idx_ch)  # Promote to recently edited
                return CLP_CH.Edit, edited_prev

        @staticmethod
        def _get_idx_changed_shape(k):
            """ User responsible for match success
            """
            return int(re.match(r'^shapes\[([0-9]+)]\.(.){2}$', k).group(1))

        def update_caliper_annotations_time(self, strt, end, figs, idx_ld):
            """ Expected to be called on every display time range change, there might not be a change

            Removes user-drawn shapes out of range if any, in the `figs` argument

            # :return Updated list of text annotations within display time range if any measurement removed,
            False otherwise
            """
            removed, idxs = _get_caliper_indices_out_of_range(  # Indices removed
                self.lst_coords,
                self.rec.count_to_pd_time(strt),
                self.rec.count_to_pd_time(end)
            )
            preserve_prev = False
            if self._idx_shape_last in idxs:  # The index of last edit is removed due to time shift
                self._idx_shape_last = None  # Caliper removed, reset
            elif self._idx_shape_last is not None:
                preserve_prev = True
                self._idx_shape_last -= sum(i < self._idx_shape_last for i in idxs)
            if removed:
                idxs.sort(reverse=True)
                self._n_mesr -= len(idxs)
                remove_by_indices(self.lst_coords, idxs)
                remove_by_indices(self.lst_ann_mesr, idxs)
                for f in figs:
                    remove_by_indices(f['layout']['shapes'], idxs)

                self._update_measurement_edit_order_after_remove(idxs)
            if self.has_measurement() and idx_ld is not None:
                self._ld_idxs_coord[-1] = idx_ld
            return removed, preserve_prev

        def clear_measurements(self):
            self._n_mesr = 0
            self.lst_coords = []
            self._ld_idxs_coord = []
            self.lst_ann_mesr = []
            self._ord_mesr_edit = []

        def highlight_mru_caliper_edit(self, figs_gra):
            """ Highlights the most recently edited shapes, for a list of figures """
            for f in figs_gra:
                for idx, shape in enumerate(f['layout']['shapes']):
                    shape['fillcolor'] = CLR_CLPR_RECT_ACT if idx == self._ord_mesr_edit[-1] else CLR_CLPR_RECT

        def get_mru_caliper_coords(self):
            """
            :return: A 2-tuple of mru leads index and 4-tuple,
            (x0, x1, y0, y1) as string representation per return of 'shape_dict_to_coords'
            if a measurement exists, None otherwise """
            if self.has_measurement():
                return self._ld_idxs_coord[-1], self.lst_coords[self._ord_mesr_edit[-1]]

        def has_measurement(self):
            return self._n_mesr > 0

        def caliper_on_display(self, idx_ld, xc, yc, x0, y0):
            for idx, coords in enumerate(self.lst_coords):
                if idx_ld == self._ld_idxs_coord[idx] and coords == (xc, yc, x0, y0):
                    return True
            return False
