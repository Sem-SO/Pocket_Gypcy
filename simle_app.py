from PyQt5 import QtCore, QtGui, QtWidgets
import requests
import pandas as pd
import matplotlib.pyplot as plt

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

"""Интерфейс"""

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(458, 240)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(190, 60, 81, 71))
        self.pushButton.setObjectName("pushButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 458, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


        self.pushButton.clicked.connect(self.graph_construct) #Нажатие на кнопку строит график

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Click on me"))

    """Логика программы"""

    def request_data(self, url, json_obj):  # Запрос информации по json
        data = requests.post(url, json=json_obj).text
        return data.splitlines()

    def get_list(self, data):  # Получение вложенного списка (по строкам)
        s = []
        for i in data:
            s.append(i.replace('"', '').split(','))
        return s

    def table_create(self, data):
        df = pd.DataFrame(data, columns=data[0])
        df = df.drop([0], axis='index')  # Удаление первой записи, так как она дублирует названия полей
        return df

    def to_data_type(self, data_frame):  # Приведение к необходимым типам данных

        int_type_columns = ['shortParQuantity', 'shortExemptParQuantity', 'totalParQuantity']
        data_frame[int_type_columns] = data_frame[int_type_columns].astype(int)  # Числовой тип

        date_type_columns = ['tradeReportDate']
        data_frame[date_type_columns] = data_frame[date_type_columns].astype('datetime64')  # Тип даты

        return data_frame

    def graph_construct(self):
        x = self.unite_function()['tradeReportDate']
        y1 = self.unite_function()['shortParQuantity']
        y2 = self.unite_function()['totalParQuantity']
        plt.title('Какой-то график')  # Название графика
        plt.xlabel('tradeReportDate')  # Название оси Х
        plt.xticks(rotation=50)  # Поворот значений оси Х вертикально
        plt.ylabel('shortParQuantity, totalParQuantity')  # Название оси У
        plt.plot(x, y1, x, y2)
        plt.show()

    def unite_function(self): #Функция, объеденяющая в себе остальные функции и возвращает итоговый DataFrame
        data = self.get_list(self.request_data(fin_url, obj))
        data_frame = self.table_create(data)  # Создание DataFrame
        df = self.to_data_type(data_frame)  # Приведение полей к необходимым типам данных

        sql_query = df.groupby(['tradeReportDate']).sum()[['shortParQuantity', 'totalParQuantity']]  # SQL запрос
        sql_query = sql_query.rename_axis(
            'tradeReportDate').reset_index()  # Перевод индексов в столбец, т.к. .groupby() делает столбец индексами

        return sql_query


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
