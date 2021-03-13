from icecream import ic

from ecg_record import EcgRecord

if __name__ == "__main__":
    rec = EcgRecord.example()
    ic(rec.COUNT_END)
