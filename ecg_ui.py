class EcgUi:
    # Keys inside `relayoutData`
    KEY_X_S = 'xaxis.range[0]'  # Start limit for horizontals axis
    KEY_X_E = 'xaxis.range[1]'
    KEY_Y_S = 'yaxis.range[0]'
    KEY_Y_E = 'yaxis.range[1]'

    KEY_X_RNG = 'xaxis.range'

    def __init__(self, parent):
        self.parn = parent

    def relayout_data_to_display_range(self, relayout_data, d_range):
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

    def relayout_data_update_display_range(self, relayout_data, d_range):
        if self.KEY_X_RNG in relayout_data:
            x_strt, x_end = relayout_data[self.KEY_X_RNG]
            d_range[0] = [
                self.parn.curr_recr.time_str_to_sample_count(x_strt),
                self.parn.curr_recr.time_str_to_sample_count(x_end)
            ]
        return d_range

    def relayout_data_update_xaxis_range(self, relayout_data, xaxis_range):
        """ Update if relayout_data change is present """
        if self.KEY_X_S in relayout_data:
            return [
                relayout_data[self.KEY_X_S],
                relayout_data[self.KEY_X_E]
            ]
        else:
            return xaxis_range
