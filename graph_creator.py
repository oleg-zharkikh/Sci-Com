from PyQt5 import QtCore, QtGui, QtWidgets
import networkx as nx
import subprocess
import sys


VISUAL_SEPARATOR = ' - '

EDGE_TITLE_COLUMN = 'Project'
EDGE_WEIGHT_COLUMN = 'ORG'

NODE_SIZE = {
    'Person': 20,
    'ORG': 40,
    'Country': 60
}

NODE_COLOR = {
    'Person': '#00FF00',
    'ORG': '#0000FF',
    'Country': '#FF0000'
}

ENTITY_BY_NODE_SIZE = {NODE_SIZE[x]: x for x in NODE_SIZE.keys()}


articles = {
    'Person': [
        ['John Smith'],
        ['David Li', 'Haori Nomokuto'],
        ['Edward Stivenson', 'David Li']
    ],
    'ORG': [
        ['MIT'],
        ['TNU', 'Flag University'],
        ['Flag University']
    ],
    'Country': [
        ['USA'],
        ['USA', 'Japan'],
        ['USA']
    ],
    'Project': [
        ['Internal study of MIT'],
        ['Cibersecurity', 'investigation'],
        ['IPROJ-1']
    ]
}


def get_unique_values(sequence):
    """Возвращает список уникальных значений из вложенных списков."""
    unique_values = set()
    for item in sequence:
        for subitem in item:
            unique_values.add(subitem.upper())
    return list(unique_values)


def gephi_open_with_appearance():
    """Открывает граф в Gephi."""
    # gephi_path = "C:/Program Files/Gephi-0.10.1/bin/gephi.exe"  # Windows
    # gephi_path = "/Applications/Gephi.app/Contents/MacOS/gephi"  # Mac
    gephi_path = "/home/oleg/Soft/gephi-0.10.1/bin/gephi"  # Linux

    # Команда для запуска Gephi в headless-режиме
    # command = [
    #     '/home/oleg/Soft/gephi-0.10.1/bin/gephi',
    #     '--run',
    #     './apply_appearance.groovy'
    # ]
    # command = [
    #     '/home/oleg/Soft/gephi-0.10.1/bin/gephi',
    #     '--console',
    #     '--run',
    #     '/home/oleg/dev/pyqt_test/apply_appearance.groovy'
    # ]
    command_open = [
        gephi_path,
        "./graph_with_appearance.gexf"
    ]
    # Запуск
    # subprocess.run(command, check=True)
    subprocess.Popen(command_open,
                     stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL,
                     start_new_session=True
                     )
    raise SystemExit()


def get_bigger_entity(entity_1, entity_2):
    """Возвращает сущность старшего порядка."""
    return ENTITY_BY_NODE_SIZE[
        max(NODE_SIZE[entity_1], NODE_SIZE[entity_2])
    ]


def get_all_pair(l1, l2):
    """Возвращает все возможные пары из списков l1 и l2."""
    result = []
    for i in l1:
        for j in l2:
            if i != j:
                result.append((i.upper(), j.upper()))
    return tuple(result)


class GraphConstructor:
    """Конструктор графа."""

    def __init__(self):
        self.selected_params = {
                'Person': 1,
                'ORG': 1,
                'Country': 0
            }
        self.possible_edges = []
        self.selected_edges = []

    def update_posible_edges(self):
        """Обновление списка возможных ребер графа."""
        new_edges = []
        for node_0 in self.selected_params.keys():
            for node_1 in self.selected_params.keys():
                pair_is_posible = (self.selected_params[node_0] and
                                   self.selected_params[node_1] and
                                   (node_0, node_1) not in new_edges and
                                   (node_1, node_0) not in new_edges)
                if pair_is_posible:
                    new_edges.append((node_0, node_1))
        self.possible_edges = new_edges
        # Коррекция уже выбранных ребер.
        if len(self.selected_edges) > 0:
            self.selected_edges = [x for x in self.selected_edges if (
                tuple(x.split(VISUAL_SEPARATOR)) in self.possible_edges or
                tuple(reversed(
                    x.split(VISUAL_SEPARATOR)
                    )) in self.possible_edges)]

    def create_graph(self):
        """Создание графа на основе выбранных параметров."""
        self.G = nx.Graph()
        # Добавление узлов.
        nodes = []
        for key in self.selected_params.keys():
            if self.selected_params[key]:
                nodes = get_unique_values(articles[key])
                for node in nodes:
                    self.G.add_node(node,
                                    size=NODE_SIZE[key],
                                    color=NODE_COLOR[key]
                                    )

        # Добавление связей.
        for edge in self.selected_edges:
            x, y = edge.split(VISUAL_SEPARATOR)
            x_list = articles[x]
            y_list = articles[y]
            for idx, item in enumerate(x_list):
                all_edges = get_all_pair(item, y_list[idx])
                edges_label = ' '.join(articles[EDGE_TITLE_COLUMN][idx])
                EDGE_WEIGHT_COLUMN = get_bigger_entity(x, y)
                edges_weight = round(1 / len(articles[EDGE_WEIGHT_COLUMN][idx]),1)
                self.G.add_edges_from(
                    all_edges,
                    label=edges_label,
                    weight=edges_weight
                )
        nx.write_gexf(self.G, "graph_with_appearance.gexf", version="1.2draft")


class Ui_MainWindow(object):
    def __init__(self):
        self.gc = GraphConstructor()

    def change_selected_params(self, checkBox, param):
        """Изменение перечня вершин графа."""
        if checkBox.checkState() > 0:
            self.gc.selected_params[param] = 1
        else:
            self.gc.selected_params[param] = 0
        self.gc.update_posible_edges()
        self.update_list_of_nodes_connections()

    def checkBox1_press(self):
        self.change_selected_params(self.checkBox, 'Person')

    def checkBox2_press(self):
        self.change_selected_params(self.checkBox_2, 'ORG')

    def checkBox3_press(self):
        self.change_selected_params(self.checkBox_3, 'Country')

    def get_selected_item(self):
        selected_indexes = self.listView.selectedIndexes()
        if not selected_indexes:
            return None
        selected_index = selected_indexes[0]
        selected_item = self.model.itemFromIndex(selected_index)
        if selected_item:
            return selected_item.text()
        return None

    def button_press(self):
        current_selected_item = self.get_selected_item()
        if (current_selected_item and
           current_selected_item not in self.gc.selected_edges):
            self.gc.selected_edges.append(current_selected_item)
            self.clear_list_view2()
            self.fill_list_view2()

    def button_finish_press(self):
        self.gc.create_graph()
        gephi_open_with_appearance()

    def update_list_of_nodes_connections(self):
        self.clear_list_view()
        self.fill_list_view()
        self.clear_list_view2()
        self.fill_list_view2()

    def fill_list_view(self):
        for item_text in self.gc.possible_edges:
            item = QtGui.QStandardItem(VISUAL_SEPARATOR.join(item_text))
            self.model.appendRow(item)

    def fill_list_view2(self):
        for item_text in self.gc.selected_edges:
            item = QtGui.QStandardItem(item_text)
            self.model2.appendRow(item)

    def clear_list_view(self):
        self.model.clear()

    def clear_list_view2(self):
        self.model2.clear()

    def setupUi(self, MainWindow):
        # GUI, генерируемый в Qt5 Designer
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(465, 533)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(20, 40, 85, 24))
        self.checkBox.setObjectName("checkBox")
        self.checkBox_2 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_2.setGeometry(QtCore.QRect(20, 60, 85, 24))
        self.checkBox_2.setObjectName("checkBox_2")
        self.checkBox_3 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_3.setGeometry(QtCore.QRect(20, 80, 85, 24))
        self.checkBox_3.setObjectName("checkBox_3")
        self.listView = QtWidgets.QListView(self.centralwidget)
        self.listView.setGeometry(QtCore.QRect(20, 150, 291, 131))
        self.listView.setObjectName("listView")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(320, 150, 80, 26))
        self.pushButton.setObjectName("pushButton")
        self.listView_2 = QtWidgets.QListView(self.centralwidget)
        self.listView_2.setGeometry(QtCore.QRect(20, 300, 291, 121))
        self.listView_2.setObjectName("listView_2")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(320, 300, 80, 26))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(20, 440, 401, 61))
        self.pushButton_3.setObjectName("pushButton_3")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 10, 361, 18))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 120, 321, 18))
        self.label_2.setObjectName("label_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Обработка формы
        # CheckBoxes:
        self.checkBox.released.connect(self.checkBox1_press)
        self.checkBox_2.released.connect(self.checkBox2_press)
        self.checkBox_3.released.connect(self.checkBox3_press)

        # ListViews:
        self.listView.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers
        )
        self.model = QtGui.QStandardItemModel()
        self.listView.setModel(self.model)

        self.listView_2.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers
        )
        self.model2 = QtGui.QStandardItemModel()
        self.listView_2.setModel(self.model2)

        # Buttons:
        self.pushButton.released.connect(self.button_press)
        self.pushButton_3.released.connect(self.button_finish_press)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow",
                                             "Настройка формирования графа"))
        self.checkBox.setText(_translate("MainWindow", "Person"))
        self.checkBox_2.setText(_translate("MainWindow", "ORG"))
        self.checkBox_3.setText(_translate("MainWindow", "Country"))
        self.pushButton.setText(_translate("MainWindow", "Добавить"))
        self.pushButton_2.setText(_translate("MainWindow", "Удалить"))
        self.pushButton_3.setText(_translate("MainWindow", "Построить граф"))
        self.label.setText(_translate("MainWindow", "Сущности для формирования узлов графа:"))
        self.label_2.setText(_translate("MainWindow", "Связи для формирования ребер графа:"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
