from ecg_record import EcgRecord

from random import randint


def get_sample_factor(strt, end):
    return max(_get_sample_factor(strt, end), 8)


def _get_sample_factor(strt, end):
    # If showing too a small range, sample_factor which is incremental steps should be at least 1
    return max((end - strt + 1) // 600, 1)


if __name__ == "__main__":
    rec = EcgRecord.example()
    END = rec.COUNT_END
    print(rec._sample_counts_acc)
    for i in range(100):
        strt = randint(0, END - 1)
        end = randint(strt, END)
        step = get_sample_factor(strt, end)
        # step = 1
        # print(strt, end, end=' ')
        # num = rec._count_indexing_num(strt, end, step)
        # print(f'size should be {num} ', end=' ')
        l1 = len(rec.get_time_values(strt, end, step))
        l2 = len(rec.get_ecg_samples(1, strt, end, step))
        print(f'{strt:>15} {end:>15} {step:>15} {l1:>15} {l2:>15}')
        assert l1 == l2

    strt, end = 19370964, 19406170
    step = 58
    print((end - strt) % step)
    print(f'difference is {end - strt}')
    print(len(rec.get_time_values(strt, end, step)), len(rec.get_ecg_samples(1, strt, end, step)))
