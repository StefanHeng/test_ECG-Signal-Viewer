import pandas as pd
import numpy as np


rng = pd.date_range(pd.Timestamp("2018-03-10 09:00"), periods=3, freq='s')
print(rng)
rng2 = rng.strftime('%r:%f')
print(rng2)
rng3 = rng.strftime('%Y-%m-%d %H:%M:%S:%f')
print(rng3)

linspace = np.linspace(0, 100, num=99)

print(3632348 / 3600 / 2000)
