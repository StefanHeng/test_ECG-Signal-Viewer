import requests

from ecg_record import *


def download_csv(csv_url):
    req = requests.get(csv_url)
    url_content = req.content
    csv_file = open('../downloaded.csv', 'wb')

    csv_file.write(url_content)
    csv_file.close()


if __name__ == "__main__":
    # csv_url = 'https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv'
    # download_csv(csv_url)
    #
    # df = pd.read_csv(csv_url)
    # fig = go.Figure([go.Scatter(x=df['Date'], y=df['AAPL.High'])])
    # fig.show()

    idx_segment = 0
    idx_lead = 0
    ecg_record = EcgRecord(DATA_PATH.joinpath(selected_record))
    key = list(ecg_record.get_segment_keys())[idx_segment]
    segment = ecg_record.get_segment(key)
    print(segment.dataset.shape)
    # time_axis = segment.get_time_axis()
    # print(time_axis.size)
    # print(time_axis[:100])
    # print(type(time_axis[0]))
    # print((time_axis / segment.sample_rate)[:100])

    # time_axis_in_ms = time_axis[:100]
    # print(pd.to_timedelta(time_axis_in_ms, unit='millisecond'))
    # print(segment.get_lead_names())

    # lead = segment.get_lead(idx_lead)
    # print(type(lead.metadata), lead.metadata)
    # print(type(lead.arr_data), lead.arr_data.shape)
    # print(lead.get_ecg_values()[:100])

    linspace = np.linspace(0, 99, num=100)
    linspace = pd.to_datetime(linspace, unit="ms")
    linspace = linspace.map(lambda t: t.strftime('%H:%M:%S:%f'))
    print(linspace)
