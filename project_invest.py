import requests
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

fin_url = 'https://api.finra.org/data/group/OTCMarket/name/regShoDaily'

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


def table_create(data):
    df = pd.DataFrame(data, columns=data[0])
    df = df.drop([0], axis='index')  # Удаление первой записи, так как она дублирует названия полей (пришлось удалить inplace=True)
    return df


def to_data_type(data_frame):  # Приведение к необходимым типам данных

    int_type_columns = ['shortParQuantity', 'shortExemptParQuantity', 'totalParQuantity']
    data_frame[int_type_columns] = data_frame[int_type_columns].astype(int)  # Числовой тип

    date_type_columns = ['tradeReportDate']
    data_frame[date_type_columns] = data_frame[date_type_columns].astype('datetime64')  # Тип даты

    return data_frame


def graph_construct(data):
    x = data['tradeReportDate']
    y1 = data['shortParQuantity']
    y2 = data['totalParQuantity']
    plt.title('Какой-то график')  # Название графика
    plt.xlabel('tradeReportDate')  # Название оси Х
    plt.xticks(rotation=50)  # Поворот значений оси Х вертикально
    plt.ylabel('shortParQuantity, totalParQuantity')  # Название оси У
    plt.plot(x, y1, x, y2)
    plt.show()


def main():
    data = get_list(request_data(fin_url, obj))
    data_frame = table_create(data)  # Создание DataFrame
    df = to_data_type(data_frame)  # Приведение полей к необходимым типам данных

    sql_query = df.groupby(['tradeReportDate']).sum()[['shortParQuantity', 'totalParQuantity']]  # SQL запрос
    sql_query = sql_query.rename_axis(
        'tradeReportDate').reset_index()  # Перевод индексов в столбец, т.к. .groupby() делает столбец индексами

    print(sql_query)

    '''Построение графика'''
    graph = graph_construct(sql_query)
    print(type(graph))


if __name__ == '__main__':
    main()
