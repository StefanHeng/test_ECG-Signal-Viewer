class EcgComment:
    """ Handles manual comment edits for EcgApp.

    Handles inter-session storage locally
    """
    def __init__(self, rec):
        self.rec = rec
