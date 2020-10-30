import vaex

import numpy as np
x = np.arange(0, 100)
ds = vaex.from_arrays("test-dataset", x=x, y=x**2)
ds.export_hdf5("/tmp/test.hdf5", progress=True)



# print(DATA_PATH.joinpath(selected_record))
# df = vaex.open(DATA_PATH.joinpath(selected_record))
# print(df)

