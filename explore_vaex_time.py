import numpy as np
import vaex as vx


date = np.array(['2009-10-12T03:31:00', '2016-02-11T10:17:34', '2015-11-12T11:34:22'], dtype=np.datetime64)
df = vx.from_arrays(date=date)
df = df.date.dt.strftime("%Y-%m")

print(df)
