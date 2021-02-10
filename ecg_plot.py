import concurrent.futures


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
    _DISPLAY_SCALE_T = 20  # #continuous time stamps to display in 1rem
    _DISPLAY_SCALE_ECG = 20  # magnitude of ecg in a 1rem
    SP_RT_READABLE = 125  # Sufficient frequency (Hz) for human differentiable graphing

    PRESERVE_UI_STATE = True  # Arbitrarily picked value
    CLR_PLT_DF = '#6AA2F9'  # Default blue by plotly
    CLR_PLT = '#2C2925'
    PRIMARY = '#FCA912'
    SECONDARY = '#2C8595'
    SECONDARY_2 = '#80B6BF'
    GRAY_0 = '#808080'  # Gray
    DEFAULT_BG = 'rgba(229, 236, 246, 0.8)'
    CLR_FONT = 'rgb(102, 102, 102)'  # Color of font

    def __init__(self, record, parent):
        self.rec = record
        self.parn = parent
        self.min_sample_step = self.rec.spl_rate // self.SP_RT_READABLE

    def get_xy_vals(self, idx_lead, strt, end):
        """
        :return: plotly line plot's x, y data points, based on current display range

        .. seealso:: `ecg_record.get_samples`
        """
        # Always take data as samples instead of entire channel, sample at at least increments of min_sample_step
        sample_factor = self.get_sample_factor(strt, end)
        return self.rec.get_time_values(strt, end, sample_factor), \
            self.rec.get_ecg_samples(idx_lead, strt, end, sample_factor)

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
                    color=self.CLR_PLT,
                    width=0.5),
            )],
            layout=dict(
                plot_bgcolor='transparent',
                dragmode='pan',
                font=dict(size=10, color=self.CLR_FONT),
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
            self.num_leads = len(self.rec.lead_nms)

            self.strt = 0  # Stays unchanged, given a record
            self.end = self.rec.COUNT_END
            self.sample_factor = self.parn.get_sample_factor(self.strt, self.end)

            self.x_vals = self.rec.get_time_values(self.strt, self.end, self.sample_factor)
            self.fig = self._get_fig_skeleton()
            self.idxs_lead = []
            # Has the corresponding y_vals been computed before
            self.been_computed = [False for i in range(self.num_leads)]
            self.lst_y_vals = [[] for i in range(self.num_leads)]

        def _get_fig_skeleton(self):
            fig = dict(
                data=[dict(
                    yaxis=self._get_yaxis_code(idx),
                    line=dict(width=0.5),
                ) for idx in range(self.num_leads)],  # Each lead has its designated slot by index
                layout=dict(
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis=dict(
                        rangeslider=dict(
                            visible=True,
                            bgcolor=self.parn.DEFAULT_BG,
                            thickness=0.4,  # Height of RangeSlider/thumbnail
                        )
                    )
                )
            )
            # Note: This `range` is different than the range argument in Figure creation, which crops off data
            fig['layout']['xaxis']['range'] = [
                self.rec.count_to_pd_time(self.parn.DISP_RNG_INIT[0][0]),
                self.rec.count_to_pd_time(self.parn.DISP_RNG_INIT[0][1])
            ]
            return fig

        @staticmethod
        def _get_yaxis_code(i):
            return f'y{i}' if i > 0 else 'y'

        def _get_y_vals(self, idx_lead):
            return self.rec.get_ecg_samples(idx_lead, self.strt, self.end, self.sample_factor)

        def add_trace(self, idxs_lead_add, override=False):
            """
            ..note:: Modifies argument list passed in
            """
            if override:
                for idx in self.idxs_lead:
                    if idx not in idxs_lead_add:
                        self._remove_trace(idx)
                self.idxs_lead = []

            idx = 0
            while idx < len(idxs_lead_add):
                idx_lead = idxs_lead_add[idx]
                if self.been_computed[idx_lead]:
                    del idxs_lead_add[idx]
                    if idx_lead not in self.idxs_lead:
                        self.fig['data'][idx_lead]['x'] = self.x_vals
                        self.fig['data'][idx_lead]['y'] = self.lst_y_vals[idx_lead]
                        self.idxs_lead.append(idx_lead)
                else:
                    idx += 1
            # Only compute lead channels not computed before
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.parn.parn.MAX_NUM_LD) as executor:
                res_y_vals = executor.map(self._get_y_vals, idxs_lead_add)
                res_y_vals = list(res_y_vals)
            # By construction, must be mutually exclusive with `idxs_lead` if override is False
            for idx, idx_lead in enumerate(idxs_lead_add):
                self.idxs_lead.append(idx_lead)
                y_vals = res_y_vals[idx]
                rang = self.parn.parn.ui.get_ignore_noise_range(y_vals)
                y_vals = self.parn.parn.ui.strip_noise(y_vals, rang[0], rang[1])
                self.fig['data'][idx_lead]['x'] = self.x_vals
                self.fig['data'][idx_lead]['y'] = self.lst_y_vals[idx_lead] = y_vals
                self.been_computed[idx_lead] = True

            self.fig['layout']['xaxis']['range'] = \
                self.parn.display_range_to_layout_range(self.parn.parn.curr_disp_rng[0])
            return self.fig

        def _remove_trace(self, idx):
            self.fig['data'][idx]['x'] = []
            self.fig['data'][idx]['y'] = []
            # self.fig['data'][idx] = dict(
            #         yaxis=self._get_yaxis_code(idx),
            #         line=dict(width=0.5),
            #         visible=False
            #     )

        def remove_trace(self, idx_idx, idx_lead):
            # TODO: Doesn't work on a single lead channel removal
            """
            :param idx_idx: Index of the lead indices in `idxs_lead`
            :param idx_lead: The lead index
            """
            # Hack, since intuitively removing the element from traces list
            # doesn't actually hide trace on the RangeSlider
            del self.idxs_lead[idx_idx]
            self._remove_trace(idx_lead)
            # for idx in self.idxs_lead:
            #     self._remove_trace(idx)
            # self.idxs_lead = []

        def __count_num_trace(self):
            # For debugging only
            return sum(('y' in d and d['y'] != []) for d in self.fig['data'])

    def display_range_to_layout_range(self, rang):
        strt, end = rang
        return [
            self.rec.count_to_pd_time(strt),
            self.rec.count_to_pd_time(end)
        ]

    def get_sample_factor(self, strt, end):
        return max(self._get_sample_factor(strt, end), self.min_sample_step)

    def _get_sample_factor(self, strt, end):
        # If showing too a small range, sample_factor which is incremental steps should be at least 1
        return max((end - strt + 1) // (self._DISPLAY_WIDTH * self._DISPLAY_SCALE_T), 1)
