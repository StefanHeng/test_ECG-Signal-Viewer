import numpy as np
import timeit

from optimize import optimize_time_conversion


def measure_np_arange(sz, num=3):
    return min(timeit.Timer(f'arr = np.arange({sz})', setup=f'import numpy as np').repeat(10, num))


def measure_np_arange_f(sz, num=3):
    return min(timeit.Timer(f'arr = np.arange({sz}) / 2', setup=f'import numpy as np').repeat(10, num))


def measure_np_arange_us(sz, num=3):
    return min(timeit.Timer(f'arr = np.arange({sz}) * 500', setup=f'import numpy as np').repeat(10, num))


def measure_np_arange_us_f(sz, num=3):
    return min(timeit.Timer(f'arr = np.arange({sz}) * 500.0', setup=f'import numpy as np').repeat(10, num))


def measure_np_linspace(sz, num=3):
    return min(timeit.Timer(f'arr = np.linspace(0, {sz-1}, {sz})', setup=f'import numpy as np').repeat(10, num))


def measure_np_linspace_f(sz, num=3):
    return min(timeit.Timer(f'arr = np.linspace(0, {sz-1}, {sz}) / 2', setup=f'import numpy as np').repeat(10, num))


def measure_np_change_type(sz, num=3):
    return min(timeit.Timer(f'arr = np.linspace(0, {sz-1}, {sz}) * 500.0', setup=f'import numpy as np').repeat(10, num))


if __name__ == "__main__":
    size = optimize_time_conversion.size
    num_per_timeit = 10
    print(measure_np_arange(size, num_per_timeit))
    print(measure_np_arange_f(size, num_per_timeit))
    print(measure_np_arange_us(size, num_per_timeit))
    print(measure_np_arange_us_f(size, num_per_timeit))
    print(measure_np_linspace(size, num_per_timeit))
    print(measure_np_linspace_f(size, num_per_timeit))
