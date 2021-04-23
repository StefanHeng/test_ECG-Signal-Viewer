import os
import json

from bisect import bisect_left

from data_link import *


class EcgComment:
    """
    Handles manual comment edits for EcgApp.

    Keeps track of comments made for a patient record file and storage between EcgApp use sessions locally

    Comments are stored in sorted order in a list
    Each comment is a 6-element list of the format `<x.center>, <y.center>, <x.0>, <y.0>, <lead_idx>, <msg>`,
    which encodes python's natural sorted order for each object

    the x values are in terms of integer ECG sample counts
    """

    def init(self, record):
        """ Update internal comments/Load potential previous comments on record change """
        self.nm = record.nm
        self.path = CURR.joinpath(f'{self.nm}_comments.json')
        if not os.path.exists(self.path) or os.stat(self.path).st_size == 0:
            with open(self.path, 'w') as f:
                json.dump([], f, indent=4)
        f = open(self.path, 'r')
        self.lst = json.load(f)
        self.n_cmts = len(self.lst)  # Number of comments
        f.close()

    def __init__(self, record):
        self.nm = None
        self.path = None
        self.lst = None
        self.n_cmts = None
        if record is not None:
            self.init(record)

    def __len__(self):
        return self.n_cmts

    def __getitem__(self, key):
        return self.lst[key]

    def update_comment(self, comment):
        """
        Can potentially modify an existing comment, or add a new one

        :param comment: 6-element list of <x.center>, <y.center>, <x.0>, <y.0>, <lead_idx>, <msg>
        """
        idx = bisect_left(self.lst, comment)
        # ic(idx, self.lst, comment)
        if idx < self.n_cmts and self.lst[idx][:-1] == comment[:-1]:  # Only difference is the message
            self.lst[idx][-1] = comment[-1]
        # Based on sorting 6-tuple, and hence sorting of the actual message, the true caliper might be before
        elif 0 <= idx-1 < self.n_cmts and self.lst[idx-1][:-1] == comment[:-1]:
            # The case where there's a previous comment made on this caliper,
            # and the new message is lexicographically larger
            self.lst[idx-1][-1] = comment[-1]
        else:
            self.lst.insert(idx, comment)
            self.n_cmts += 1
        self.flush()

    def flush(self):
        """ Writes all changes made to comments into original JSON file """
        config = open(self.path, 'w')
        json.dump(self.lst, config, indent=4)
        config.close()

    def get_comment_list(self, idxs_lead, strt=-1, end=-1, verbose=False):
        """ Get the list of comments in sorted order
        If strt and end are specified as sample counts, only those comments within range are returned

        If verbose is False, return comment of 3-tuple:  <x.center>, <lead_idx>, <msg>), otherwise
        return full comment of 6-tuple

        :return 2-tuple of (indices of the comments, the comment in internal list storage
        """
        lst = []
        idxs = []
        idx_strt, idx_end = 0, self.n_cmts
        if strt != -1 and end != -1:
            idx_strt = bisect_left(self.lst, [strt] + [-1] * 5)
            idx_end = bisect_left(self.lst, [end] + [2 ** 20] * 5)  # End should be inclusive enough
        for idx, row in enumerate(self.lst[idx_strt:idx_end]):
            if row[-2] in idxs_lead:
                idxs.append(idx + idx_strt)
                if verbose:
                    lst.append(row)
                else:
                    lst.append([row[0], row[-2], row[-1]])
        return idxs, lst
