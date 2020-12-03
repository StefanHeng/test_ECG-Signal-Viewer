import h5py
import json
import numpy as np
import pandas as pd

from bisect import bisect_left, bisect_right

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from math import floor
from copy import deepcopy

from memory_profiler import profile

from dev_file import *
from ecg_app import EcgApp
from ecg_record import EcgRecord

from memory_profiler import profile


# @profile
def test_import():
    import h5py
    import json
    import numpy as np
    # import pandas as pd
    from pandas import Timestamp, Timedelta, to_timedelta, Series

    from bisect import bisect_left, bisect_right

    import dash
    import dash_core_components as dcc
    import dash_html_components as html
    from dash.dependencies import Input, Output, State

    from math import floor
    from copy import deepcopy

    from memory_profiler import profile

    import dev_file
    from ecg_app import EcgApp
    from ecg_record import EcgRecord
    print(1)


@profile
def test_h5py_mem_map():
    r = EcgRecord.example()
    # a = r.get_samples(3, 3000, 4000, 8)
    print(r._seg_keys)
    dset = r.record[r._seg_keys[3]]
    a = dset[5, :400000]
    print(dset.shape, type(dset))


if __name__ == "__main__":
    # test_import()

    test_h5py_mem_map()
