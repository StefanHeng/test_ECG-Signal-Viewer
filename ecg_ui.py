class EcgUi:
    # Keys inside `relayoutData`
    KEY_X_S = 'xaxis.range[0]'  # Start limit for horizontals axis
    KEY_X_E = 'xaxis.range[1]'
    KEY_Y_S = 'yaxis.range[0]'
    KEY_Y_E = 'yaxis.range[1]'

    KEY_X_RNG = 'xaxis.range'

    def __init__(self, parent):
        self.parn = parent

    def get_display_range(self, layout_fig):
        """
        :param layout_fig: Layout of Plotly graph object
        :return: 2*2 List of List containing x and y axis range
        """
        x_range = layout_fig['xaxis']['range']
        return [[
            self.parn.curr_recr.time_str_to_sample_count(x_range[0]),
            self.parn.curr_recr.time_str_to_sample_count(x_range[1])],
            layout_fig['yaxis']['range']
        ]

    def get_x_display_range(self, layout_fig):
        x_range = layout_fig['xaxis']['range']
        return [
            self.parn.curr_recr.time_str_to_sample_count(x_range[0]),
            self.parn.curr_recr.time_str_to_sample_count(x_range[1])
        ]

    def relayout_data_to_display_range(self, layout_fig, disp_rng):
        """
        Modifies parameter passed in, updates horizontal, vertical plot limit in terms of sample count
        Due to plotly graph_obj internal storage format of `relayoutData`

        :param layout_fig:  Horizontal, vertical plot limit,  as str representation of pandas timestamp
        :param disp_rng: Previous sample count range
        """
        # print(f'In update d_range, {layout_fig}')
        if self.KEY_X_S in layout_fig:
            disp_rng[0] = [
                self.parn.curr_recr.time_str_to_sample_count(layout_fig[self.KEY_X_S]),
                self.parn.curr_recr.time_str_to_sample_count(layout_fig[self.KEY_X_E])
            ]
        # if self.KEY_Y_S in layout_fig:
        #     disp_rng[1] = [
        #         self.parn.curr_recr.time_str_to_sample_count(layout_fig[self.KEY_Y_S]),
        #         self.parn.curr_recr.time_str_to_sample_count(layout_fig[self.KEY_Y_E])
        #     ]

    def relayout_data_update_display_range(self, layout_fig, disp_rng):
        if self.KEY_X_RNG in layout_fig:
            x_strt, x_end = layout_fig[self.KEY_X_RNG]
            disp_rng[0] = [
                self.parn.curr_recr.time_str_to_sample_count(x_strt),
                self.parn.curr_recr.time_str_to_sample_count(x_end)
            ]
        return disp_rng

    def relayout_data_update_xaxis_range(self, layout_fig, xaxis_range):
        """ Update if relayout_data change is present """
        if self.KEY_X_S in layout_fig:
            return [
                layout_fig[self.KEY_X_S],
                layout_fig[self.KEY_X_E]
            ]
        else:
            return xaxis_range
