import json
import requests
import pandas as pd

shit_url = 'https://api.finra.org/data/group/OTCMarket/name/regShoDaily'

obj = {
    "fields": [
        # "reportingFacilityCode",
        "tradeReportDate",
        "securitiesInformationProcessorSymbolIdentifier",
        "shortParQuantity",
        "shortExemptParQuantity",
        "totalParQuantity",
        "marketCode",
    ],
    "compareFilters": [
        {
            "compareType": "equal",
            "fieldName": "securitiesInformationProcessorSymbolIdentifier",
            "fieldValue": "GTHX"
        },
        {
            "compareType": "greater",
            "fieldName": "tradeReportDate",
            "fieldValue": "2021-04-07"
        }
    ]
}


def request_data(url, json_obj):  # Запрос информации по json
    data = requests.post(url, json=json_obj).text
    return data.splitlines()


def get_list(data):  # Получение вложенного списка (по строкам)
    s = []
    for i in data:
        s.append(i.replace('"', '').split(','))
    return s


def to_data_type(data_frame):  # Приведение к необходимым типам данных

    int_type_columns = ['shortParQuantity', 'shortExemptParQuantity', 'totalParQuantity']
    data_frame[int_type_columns] = data_frame[int_type_columns].astype(int)  # Числовой тип

    date_type_columns = ['tradeReportDate']
    data_frame[date_type_columns] = data_frame[date_type_columns].astype('datetime64')  # Тип даты

    return data_frame


def main():
    data = get_list(request_data(shit_url, obj))
    df = pd.DataFrame(data, columns=data[0])
    df.drop([0], axis='index', inplace=True)  # Удаление первой записи, так как она дублирует названия полей
    df = to_data_type(df)  # Приведение к необходимым типам данных
    # print(df)
    # print(df.info())

    print(df.groupby(['tradeReportDate']).sum()[['shortParQuantity', 'totalParQuantity']])  # SQL запрос


if __name__ == '__main__':
    main()
