import vaex
import numpy as np
import random

# df = vaex.open('s3://vaex/taxi/yellow_taxi_2015_f32s.hdf5?anon=true')
#
# print(f'number of rows: {df.shape[0]:,}')
# print(f'number of columns: {df.shape[1]}')
#
# long_min = -74.05
# long_max = -73.75
# lat_min = 40.58
# lat_max = 40.90
#
# df.plot(df.pickup_longitude, df.pickup_latitude, f="log1p", limits=[[-74.05, -73.75], [40.58, 40.90]], show=True)


def vx_df_eg(num=64, prime=97):
    t = np.arange(num) + 1
    f1 = t ** 2
    f2 = np.log(t)
    f3 = random.sample(range(0, 99), num)
    f4 = t ** 2 - 10 * t + 3
    f5 = np.vectorize(lambda x: np.math.factorial(x) % prime ** 2)(t)
    d = {'t': t, 'f1': f1, 'f2': f2, 'f3': f3, 'f4': f4, 'f5': f5}
    return vaex.from_dict(d)


if __name__ == "__main__":
    df = vx_df_eg()
    print(df)
    print(df.t, type(df.t))
    print(type(df.f1.values))
    print(df.f1.values)
    print(df.mean(df.t))
    print(df.count())
    print(df.mean(df.f1))
    print()

    print(df.select(df.f3 > 50))  # So no return
    print(df.evaluate(df.f3, selection=True))  # So I need to call selection before using selection in function keyword
    print(df.evaluate(df.f3, selection=False))
    # print(df)  # so stays unchanged
    print(df.mean(df.f5, selection=True))
    print(df.mean(df.f5, selection=False))
    print()

    print(df.count(binby=df.t, shape=8))
    print(df.count(binby=df.t, limits='50%', shape=8))
    print(df.count(binby=df.t, limits=[-10, 10], shape=8))
    print(df.count(binby=df.t, limits=[0, 5], shape=8))
    print(df.count(binby=df.t, limits=[10, -10], shape=8))
    print(df.count(binby=df.t, limits=[0, 2], shape=8))
    print(df.count('f1', binby=df.f1, limits='minmax', shape=4))
    print(df.count(df.f5, binby=df.f5, limits='minmax', shape=16))
    print()

    print(df.mean(df.t, shape=2))
    print(df.mean(df.t, binby=df.t, shape=2))
    print(df.mean(df.t, binby=df.t, shape=4))
    print(df.mean(df.t, binby=df.t, limits=[1, 8], shape=2))
    print(df.mean(df.t, binby=df.f1, shape=2))
    print(df.mean(df.t, binby=df.f2, shape=2))
    print(df.mean(df.f1, binby=df.f1, shape=16))
    print(df.mean(df.f1, binby=df.f1, limits=[0, 10], shape=2))
    print(df.mean(df.f1, binby=df.f1, limits=[0, 50], shape=2))
    print()

    print(df.count(binby=[df.t, df.f1], limits=[[-10, 10], [-10, 20]], shape=(4, 16)))
    print(df.count(binby=[df.t, df.f1], limits=[[-10, 10], [-10, 20]], shape=(16, 4)))
    print(df.count(binby=[df.t, df.f1], shape=(8, 4)))


