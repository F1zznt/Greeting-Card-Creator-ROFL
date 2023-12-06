import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QIntValidator

from PIL import Image
from io import BytesIO
import sqlite3
import base64
import json
from datetime import datetime
import time
import shutil
import requests

from printing import Color, AddText


class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        print(data)
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)


class Ui_DataBase(QWidget):
    def __init__(self):
        super().__init__()
        self.app = QtWidgets.QApplication(sys.argv)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(872, 561)
        MainWindow.setMaximumSize(872, 561)
        MainWindow.setMinimumSize(872, 561)
        screen_geometry = self.app.desktop().screenGeometry()
        MainWindow.setGeometry(screen_geometry.width() - 420 - 308 - 872,
                               screen_geometry.height() - (594 + int((screen_geometry.height()
                                                                      / 100) * 3.81)), 872, 561)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background-color:#42aaff")

        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(0, 0, 761, 561))
        self.tableWidget.setMinimumSize(QtCore.QSize(872, 561))
        self.tableWidget.setMaximumSize(QtCore.QSize(872, 561))
        self.tableWidget.setObjectName("tableView")
        self.tableWidget.verticalHeader().setVisible(False)

        self.conn = sqlite3.connect("mydatabase.db")
        query = "SELECT * FROM mytable"
        cursor = self.conn.execute(query)
        row_len = []
        for i in cursor:
            row_len.append(len(i))
        self.col_num = max(row_len)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(int(self.col_num))

        cursor = self.conn.execute(query)
        for row, row_data in enumerate(cursor):
            self.tableWidget.insertRow(row)
            for col, col_data in enumerate(row_data):
                self.tableWidget.setItem(row, col, QtWidgets.QTableWidgetItem(str(col_data)))

        self.tableWidget.setHorizontalHeaderLabels(["id", "prompt", "text", "width", "height", "image"])
        self.tableWidget.setStyleSheet("QTableWidget{background: #6495ed; color: white;}")
        self.tableWidget.setColumnWidth(0, 20)
        self.tableWidget.setColumnWidth(1, 350)
        self.tableWidget.setColumnWidth(2, 350)
        self.tableWidget.setColumnWidth(3, 30)
        self.tableWidget.setColumnWidth(4, 30)
        self.tableWidget.setColumnWidth(5, 50)
        self.conn.close()

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("History", "History"))


class Ui_Form(QWidget):
    def __init__(self):
        super().__init__()

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1255, 904)
        Form.setStyleSheet("background-color: rgb(57,61,65)")
        img = Image.open("image_with_text.png")
        width = img.width
        height = img.height

        Form.setGeometry(0, 0, width + 20, height + 110)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 10, width, height))
        self.label.setStyleSheet("text-align: center;")
        self.label.setPixmap(QtGui.QPixmap("image_with_text.png"))
        self.label.setObjectName("label")

        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(((width + 20) // 2) - 220, height + 40, 441, 41))
        self.pushButton.setText("СКАЧАТЬ ДЛЯ ОТПРАВКИ ВНУЧКУ")
        self.pushButton.setStyleSheet("\n"
                                      "QPushButton {\n"
                                      "    background-color: #39306B;  \n"
                                      "    color: #ffffff;  \n"
                                      "    border: 2px solid #9694A5;  \n"
                                      "    padding: 10px 20px;  \n"
                                      "    font-size: 16px;  \n"
                                      "    cursor: pointer;  \n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:hover {\n"
                                      "    background-color: #9694A5;\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:pressed {\n"
                                      "    animation: explode 0.5s forwards;  \n"
                                      "}\n"
                                      "\n"
                                      "@keyframes explode {\n"
                                      "    0% {\n"
                                      "        transform: scale(1);  \n"
                                      "    }\n"
                                      "    100% {\n"
                                      "        transform: scale(1.5);  \n"
                                      "        opacity: 0;  \n"
                                      "    }\n"
                                      "}\n"
                                      "")
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.save_picture)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def save_picture(self):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        image_path = "image_with_text.png"
        destination_path = os.path.join(desktop_path, "Открыточка.png")
        shutil.copyfile(image_path, destination_path)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton.setText(_translate("Form", "СКАЧАТЬ ДЛЯ ОТПРАВКИ ВНУЧКУ"))

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Your Greeting Card"))


class Ui_CreateMemes(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.app = QtWidgets.QApplication(sys.argv)
        self.prompts = {
            1: "Создай изображение, на котором морская черепаха учится играть на саксофоне.",
            2: "Покажи, как выглядел бы космический бар на поверхности Луны.",
            3: "Изобрази велосипед с пальто и бананами вместо колес.",
            4: "Создай футуристический город, где дельфины управляют метро.",
            5: "Изобрази лес, где деревья выглядят как сверкающие радуги.",
            6: "Покажи, как выглядели бы жирафы, если бы у них были шарики вместо шеи.",
            7: "Создай изображение, на котором пингвины играют в бейсбол на антарктическом льду.",
            8: "Изобрази дерево с ветвями из конфет и леденцов.",
            9: "Покажи робота, который учит медведей танцевать брейк-данс.",
            10: "Создай пейзаж с летающими слонами и шариками мыльных пузырей.",
            11: "Изобрази дракона, который исполняет сказочные песни на сцене.",
            12: "Покажи котенка, который управляет магическим поездом.",
            13: "Создай изображение, на котором пингвины катаются на горках из мороженого.",
            14: "Изобрази землю, где дождь падает из конфетных облаков.",
            15: "Покажи, как выглядел бы зебра-баркод.",
            16: "Создай город, где дома выполнены в виде больших шляп.",
            17: "Изобрази море, в котором рыбы плавают в чашках для кофе.",
            18: "Покажи, как выглядел бы огромный билет на театральное представление для китов.",
            19: "Дерево",
            20: "Изобрази солнце, которое улыбается и печет пиццу.",
            21: "Покажи летучих мышей, которые устраивают гонки на самолетах.",
            22: "Создай озеро, где вместо воды - лимонад.",
            23: "Изобрази гирбилиссов, которые путешествуют по миру на воздушных шарах.",
            24: "Покажи, как выглядел бы паучок с банановой ножкой.",
            25: "Создай ферму, где пингвины выращивают шарики для бильярда.",
            26: "Изобрази снеговика, который собирает снег в ведре.",
            27: "Покажи, как выглядели бы кролики, если бы они были высокошкольными преподавателями.",
            28: "Создай изображение, на котором дельфины учатся ездить на велосипедах в море.",
            29: "Изобрази космическую станцию, которая выглядит как большой торт.",
            30: "Покажи, как выглядели бы пчелы, если бы они носили маленькие шляпки и бабочки."
        }
        self.congratulations = {
            1: "С днем рождения! Ты становишься мудрее и старше, но хотя бы не сморщиваешься!",
            2: "Поздравляем с днем рождения! Ты как вино, с возрастом только гораздо дороже!",
            3: "Со дня рождения! Ты такой взрослый, что даже кролик Энерджайзер завидует твоей энергии!",
            4: "День рождения — это всего лишь отметка в календаре, а ты как всегда - вне времени и пространства!",
            5: "Счастья и долголетия! Для тебя каждый день — это как праздник... и снова праздник!",
            6: "Поздравляю с новым этапом жизни! Теперь ты можешь носить носки на руках и говорить, что это последний "
               "писк моды.",
            7: "С днем рождения! Пусть вся твоя жизнь будет такой же забавной, как этот поздравительный текст!",
            8: "Возраст — это всего лишь число, а ты — настоящая живая легенда!",
            9: "С днем рождения! Ты становишься старше, но твой юмор остается вечно молодым!",
            10: "Поздравляю с днем рождения! Ты как дракон: год за годом, и все вокруг восхищаются тобою!",
            11: "Счастья и удачи! Ты так молод, что даже антиквариатные вещи завидуют твоей свежести!",
            12: "Поздравляем с днем рождения! Ты стареешь, но твоя душа остается вечно молодой!",
            13: "С Днем Рождения! Ты как вино, стареешь с годами, но становишься крепче!",
            14: "Поздравляем с днем рождения! Ты стареешь, но твоя улыбка сверкает ярче!",
            15: "Счастья, радости и молодости! Возраст всего лишь цифры, а ты - вечно молодая душа!",
            16: "Поздравляем с днем рождения! Ты стареешь, но твоя энергия не угасает!",
            17: "С днем рождения! Ты как кофе - с годами только крепче и вкуснее!",
            18: "Поздравляю с днем рождения! Ты как вино: чем старше, тем лучше!",
            19: "Счастья и радости в твой особенный день! Возраст — это лишь количество прожитых приключений!",
            20: "С днем рождения! Ты как алмаз: непреходящая ценность и бриллиантовый юмор!",
            21: "Поздравляем с днем, когда ты стал старше на целый день!",
            22: "Ты не стареешь, ты только увеличиваешь свою ценность на антикварном рынке!",
            23: "С днем рождения! Теперь ты ближе к пенсии, чем к детству.",
            24: "Поздравляем с твоим личным новым годом!",
            25: "Как говорят, с возрастом вино становится только лучше. На твоем месте я бы переключился на вино.",
            26: "Счастья, здоровья и огромного количества космических коров!",
            27: "Ты уже настолько зрел, что можешь даже пыль собирать!",
            28: "Поздравляю с днем, когда ты стал старше, но не обязательно умнее.",
            29: "Возраст — это всего лишь число, и, кстати, у меня его нет.",
            30: "Счастья и смеха, чтобы ты всегда забывал, сколько тебе лет! ",
            0: "Твоя улыбка - самое ценное, что у тебя есть, потому что она полна золотых зубов"
        }

    def setupUi(self, CreateMemes):
        CreateMemes.setObjectName("CreateMemes")
        CreateMemes.resize(307, 575)
        self.centralwidget = QtWidgets.QWidget(CreateMemes)
        screen_geometry = self.app.desktop().screenGeometry()
        CreateMemes.setGeometry(screen_geometry.width() - 420 - 308,
                                screen_geometry.height() - (594 + int((screen_geometry.height()
                                                                       / 100) * 3.81)), 308, 575)
        self.centralwidget.setMinimumSize(QtCore.QSize(307, 575))
        self.centralwidget.setMaximumSize(QtCore.QSize(307, 575))
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 0, 308, 575))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("mspaint_bPrbQKy8H7.png"))
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(0, 40, 301, 151))
        self.pushButton.setStyleSheet("border-radius: 15px;\n"
                                      "margin:20px auto;\n"
                                      "color: #FFFFFF;\n"
                                      " display: block;\n"
                                      "   font:bold 16px arial;\n"
                                      "    line-height: 35px;\n"
                                      "    text-align: center;\n"
                                      "    text-decoration: none;\n"
                                      "border-radius: 15px;        background:  rgb(215,200,190);\n"
                                      "    transition: all 0.5s linear 0s;\n"
                                      "        border-bottom: 4px solid #ccc;")
        self.pushButton.setObjectName("pushButton")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setPlaceholderText("        width")
        validator = QIntValidator()
        self.lineEdit.setValidator(validator)
        self.lineEdit.setGeometry(QtCore.QRect(20, 510, 111, 41))
        self.lineEdit.setStyleSheet("color: #FFFFFF;\n"
                                    "display: block;\n"
                                    "font:bold 16px arial;\n"
                                    "line-height: 35px;\n"
                                    "text-align: center;\n"
                                    "text-decoration: none;\n"
                                    "border-radius: 15px;       \n"
                                    "background: #D07A52;\n"
                                    "transition: all 0.5s linear 0s;")
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setPlaceholderText("         height")
        validator_2 = QIntValidator()
        self.lineEdit_2.setValidator(validator_2)
        self.lineEdit_2.setGeometry(QtCore.QRect(170, 510, 121, 41))
        self.lineEdit_2.setStyleSheet("color: #FFFFFF;\n"
                                      "display: block;\n"
                                      "font:bold 16px arial;\n"
                                      "line-height: 35px;\n"
                                      "text-align: center;\n"
                                      "text-decoration: none;\n"
                                      "border-radius: 15px;       \n"
                                      "background: #D07A52;\n"
                                      "transition: all 0.5s linear 0s;")
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_3.setPlaceholderText("     come up with a creative promt")
        self.lineEdit_3.setGeometry(QtCore.QRect(20, 310, 271, 71))
        self.lineEdit_3.setStyleSheet("color: #FFFFFF;\n"
                                      "display: block;\n"
                                      "font:bold 16px arial;\n"
                                      "line-height: 35px;\n"
                                      "text-align: center;\n"
                                      "text-decoration: none;\n"
                                      "border-radius: 15px;       \n"
                                      "background: #D07A52;\n"
                                      "transition: all 0.5s linear 0s;")
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_4 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_4.setPlaceholderText("  come up with a creative greeting")
        self.lineEdit_4.setGeometry(QtCore.QRect(20, 410, 271, 71))
        self.lineEdit_4.setStyleSheet("color: #FFFFFF;\n"
                                      "display: block;\n"
                                      "font:bold 16px arial;\n"
                                      "line-height: 35px;\n"
                                      "text-align: center;\n"
                                      "text-decoration: none;\n"
                                      "border-radius: 15px;       \n"
                                      "background: #D07A52;\n"
                                      "transition: all 0.5s linear 0s;")
        self.lineEdit_4.setObjectName("lineEdit_4")
        CreateMemes.setCentralWidget(self.centralwidget)

        self.retranslateUi(CreateMemes)
        QtCore.QMetaObject.connectSlotsByName(CreateMemes)

        self.pushButton.clicked.connect(self.generate)
        self.pushButton.clicked.connect(self.open_window)

    def retranslateUi(self, CreateMemes):
        _translate = QtCore.QCoreApplication.translate
        CreateMemes.setWindowTitle(_translate("CreateMemes", "Create Greeting Card"))
        self.pushButton.setText(_translate("CreateMemes", "GENERATE"))
        self.lineEdit.setText(_translate("CreateMemes", ""))
        self.lineEdit_2.setText(_translate("CreateMemes", ""))
        self.lineEdit_3.setText(_translate("CreateMemes", ""))
        self.lineEdit_4.setText(_translate("CreateMemes", ""))

    def append_to_database(self, info_dict: dict):
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mytable (
                id INTEGER PRIMARY KEY,
                prompt TEXT,
                text TEXT,
                width INTEGER,
                height INTEGER,
                image BLOB)''')

        cursor.execute('''INSERT INTO mytable (prompt, text, width, height, image)
                                VALUES (?, ?, ?, ?, ?)''',
                       (
                           info_dict["prompt"], info_dict["text"], info_dict["width"], info_dict["height"],
                           self.path_file))
        conn.commit()
        conn.close()

    @staticmethod
    def days_until_new_year():
        current_date = datetime.now()
        current_year = current_date.year
        new_year_date = datetime(current_year + 1, 1, 1)
        days_until_new_year_ = (new_year_date - current_date).days
        return days_until_new_year_

    def generate_promt(self) -> str:
        current_time = time.localtime()
        current_second = current_time.tm_sec
        time_to_key = int(current_second / 2)
        print(self.prompts[time_to_key])
        return self.prompts[time_to_key]

    def generate_congratulation(self) -> str:
        current_time = time.localtime()
        current_second = current_time.tm_sec
        time_to_key = int(current_second / 2)
        print(self.congratulations[time_to_key])
        return self.congratulations[time_to_key]

    def create_picture(self, promt: str, width: int, height: int) -> str:
        api = Text2ImageAPI('https://api-key.fusionbrain.ai/', '6F37C428933BECE0321B5290607A1BBB',
                            'A5F49A73323C23A569A210458CD84440')
        model_id = api.get_model()
        uuid = api.generate(promt, model_id, width=width, height=height)
        images = api.check_generation(uuid)

        self.path_file = f"data:image/png;base64,{images[0]}"
        print(self.path_file)
        return self.path_file  # ['data:image/png;base64,']

    @staticmethod
    def download_image(base64_data: str):
        image_data = base64_data.split(",")[1]
        image_binary_data = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_binary_data))
        image.save("url2picture.png")

        return image

    def open_window(self):
        self.Form = QtWidgets.QWidget()
        self.ui.setupUi(self.Form)
        self.Form.show()

    def generate(self) -> None:
        prompt_text = self.lineEdit_3.text()
        greeting_text = self.lineEdit_4.text()
        if not prompt_text:
            prompt_text = self.generate_promt()

        if not greeting_text:
            greeting_text = self.generate_congratulation()

        try:
            width_value = int(self.lineEdit.text())
        except ValueError:
            width_value = 1024

        try:
            height_value = int(self.lineEdit_2.text())
        except ValueError:
            height_value = 512

        self.info_dict = {"prompt": prompt_text, "text": greeting_text, "width": width_value, "height": height_value}
        print(self.info_dict)

        image: str = "url2picture.png"

        print("начал генерацию")
        url: str = self.create_picture(self.info_dict["prompt"], self.info_dict["width"], self.info_dict["height"])
        print("сгенерено")

        self.download_image(url)
        print("скачано")

        printing = Color()
        painting = AddText()
        color: tuple = printing.average_color(image)
        contrast_color: tuple = printing.find_contrast_color(color)
        painting.add_text(image, self.info_dict["text"], contrast_color)
        #
        self.append_to_database(self.info_dict)


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_CreateMemes()
        self.db = Ui_DataBase()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(420, 594)
        MainWindow.setMinimumSize(420, 594)
        MainWindow.setMaximumSize(420, 594)

        screen_geometry = app.desktop().screenGeometry()
        MainWindow.setGeometry(screen_geometry.width() - 420,
                               screen_geometry.height() - (594 + int((screen_geometry.height() / 100) * 3.81)),
                               420, 594)

        MainWindow.setStyleSheet(
            "background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 rgba(33, 37, 70, 1), stop:0.3 "
            "rgba(33, 37, 70, 1), stop:1 rgba(87, 39, 153, 1))")
        MainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.Russian, QtCore.QLocale.Kyrgyzstan))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(30, 420, 361, 151))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setStyleSheet(
            "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #D66468, stop: 1 #F49A59);\n"
            " border-radius: 15px;\n"
            " color: white; \n"
            "font-size: 24px;\n"
            "font-family: -apple-system, BlinkMacSystemFont, \\\"Segoe UI\\\", \\\"Roboto\\\", \\\"Oxygen-Sans\\\", "
            "\\\"Ubuntu\\\", \\\"Cantarell\\\", \\\"Fira Sans\\\", \\\"Droid Sans\\\", \\\"Helvetica Neue\\\","
            " sans-serif;\n"
            "text-align: left;\n"
            "padding-left: 20px;")

        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(30, 240, 361, 151))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setStyleSheet(
            "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #1859B0, stop: 1 #0ABCD4);\n"
            "            border-radius: 15px;\n"
            "            color: white; \n"
            "            font-size: 24px;\n"
            "font-family: -apple-system, BlinkMacSystemFont, \\\"Segoe UI\\\", \\\"Roboto\\\", \\\"Oxygen-Sans\\\", "
            "\\\"Ubuntu\\\", \\\"Cantarell\\\", \\\"Fira Sans\\\", \\\"Droid Sans\\\", \\\"Helvetica Neue\\\", "
            "sans-serif;\n"
            "text-align: left;\n"
            "            padding-left: 20px;")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 0, 201, 31))
        self.label.setObjectName("label")
        self.label.setStyleSheet("background: transparent; \n"
                                 "color: white;\n"
                                 "font-size: 32px; \n"
                                 "font-family: -apple-system, BlinkMacSystemFont, \\\"Segoe UI\\\", \\\"Roboto\\\", "
                                 "\\\"Oxygen-Sans\\\", \\\"Ubuntu\\\", \\\"Cantarell\\\", \\\"Fira Sans\\\", "
                                 "\\\"Droid Sans\\\",\\\"Helvetica Neue\\\", sans-serif;")

        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(30, 60, 361, 151))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setStyleSheet("background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #C943D2, "
                                        "stop: 1 #6124AE);\n"
                                        "border-radius: 15px;\n"
                                        "color: white; \n"
                                        "font-size: 24px;\n"
                                        "font-family: -apple-system, BlinkMacSystemFont, \\\"Segoe UI\\\", "
                                        "\\\"Roboto\\\", \\\"Oxygen-Sans\\\", \\\"Ubuntu\\\", \\\"Cantarell\\\", "
                                        "\\\"Fira Sans\\\", \\\"Droid Sans\\\", \\\"Helvetica Neue\\\", sans-serif;\n"
                                        "text-align: left;\n"
                                        "text-align: center;\n"
                                        "padding-bottom: 45px;\n"
                                        "")

        self.lcdNumber = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumber.setGeometry(QtCore.QRect(180, 130, 71, 23))
        self.lcdNumber.setStyleSheet("background-color:#7608AA")
        self.lcdNumber.setObjectName("lcdNumber")
        self.lcdNumber.display(self.ui.days_until_new_year())

        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(50, 330, 200, 16))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setStyleSheet("background: transparent; \n"
                                        "color: white;\n"
                                        "font-size: 12px; \n"
                                        "font-family: -apple-system, BlinkMacSystemFont, "
                                        "\\\"Segoe UI\\\", \\\"Roboto\\\", \\\"Oxygen-Sans\\\", "
                                        "\\\"Ubuntu\\\", \\\"Cantarell\\\", \\\"Fira Sans\\\", "
                                        "\\\"Droid Sans\\\",\\\"Helvetica Neue\\\", sans-serif;")

        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setGeometry(QtCore.QRect(50, 500, 200, 31))
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setStyleSheet("background: transparent; \n"
                                        "color: white;\n"
                                        "font-size: 12px; \n"
                                        "font-family: -apple-system, BlinkMacSystemFont, \\\"Segoe UI\\\","
                                        " \\\"Roboto\\\", \\\"Oxygen-Sans\\\", \\\"Ubuntu\\\", \\\"Cantarell\\\","
                                        " \\\"Fira Sans\\\", \\\"Droid Sans\\\",\\\"Helvetica Neue\\\", sans-serif;")

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.pushButton.clicked.connect(self.open_window)
        self.pushButton_5.clicked.connect(self.open_window)
        self.pushButton_2.clicked.connect(self.open_history)
        self.pushButton_4.clicked.connect(self.open_history)

    def open_window(self):
        self.CreateMemes = QtWidgets.QMainWindow()
        self.ui.setupUi(self.CreateMemes)
        self.CreateMemes.show()

    def open_history(self):
        self.HistoryWindow = QtWidgets.QMainWindow()
        self.db.setupUi(self.HistoryWindow)
        self.HistoryWindow.show()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "YRP - application"))
        self.pushButton.setText(_translate("MainWindow", "Create GCard"))
        self.pushButton_2.setText(_translate("MainWindow", "Check History"))
        self.label.setText(_translate("MainWindow", "Сreate Picture"))
        self.pushButton_3.setText(_translate("MainWindow", "How many days until  NY:"))
        self.pushButton_4.setText(_translate("MainWindow", "view the history of your requests"))
        self.pushButton_5.setText(_translate("MainWindow", "create your own greeting card"))


app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()

sys.exit(app.exec_())
