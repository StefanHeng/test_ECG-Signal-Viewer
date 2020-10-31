from ecg_record import EcgRecord


class EcgPlot:
    """Handles plotting among a single `record`, or surgery.
    """

    def __init__(self, path):
        self.ecg_record = EcgRecord(path)
        # Ad-hoc values for now, in the future should be calculated from device info
        # Default starting point, in the future should be retrieved from user
        self.display_scale_t = 20  # #continuous time stamps to display in 1rem
        self.display_scale_ecg = 20  # magnitude of ecg in a 1rem
        self.display_range = [0, 10000]  # based on #samples, one-to-one correspondence with time by `sample_rate`

    # def get_plot(self):

    # def get_

