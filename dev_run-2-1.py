# from memory_profiler import profile

from ecg_app import *


# @profile
def main():
    ecg_app = EcgApp(__name__)
    ecg_app.app.title = "Dev test run"

    ecg_app.run(debug=True)
    # ecg_app.run(debug=False)


if __name__ == "__main__":
    main()
