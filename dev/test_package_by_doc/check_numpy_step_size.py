import numpy as np

from random import random

import unittest


def count_indexing_num(strt, end, step):
    """Counts the number of elements as result of numpy array indexing """
    num = (end - strt) // step
    if (end - strt) % step != 0:
        num += 1
    return num


if __name__ == "__main__":
    sz = 1000
    arr = np.arange(sz)
    for i in range(100):
        strt = int(random() * sz)
        end = int(random() * sz)
        step = int(random() * 30) + 1
        if strt > end:
            strt, end = end, strt
        res = arr[strt:end:step]
        size = count_indexing_num(strt, end, step)
        print(f'Array indexing on strt <- {strt}, end <- {end}, step <- {step} has size: [{res.shape[0]}] and func returns [{size}]')
        assert(res.shape[0] == size)

