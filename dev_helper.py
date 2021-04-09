record_nm = 'LOG_DHR50526570_09000e6f-001.h5'
record_p_nm = f'{record_nm[:-3]}_preprocessed.hdf5'

KW_DEV = '[DEV]_'


def dev(s):  # Annotate with dev keyword
    return KW_DEV + s
