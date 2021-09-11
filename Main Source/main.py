from func import *

class MainWindow(QMainWindow):
    def __init__(self):
        ###==SETUP==BEGIN==###
        QMainWindow.__init__(self, flags=Qt.FramelessWindowHint)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.settings = Settings.settings
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_login)
        self.key = str
        self.encFunc = EncryptFunctions()
        ###==SETUP==END==###

        ###==MOVE_FRAME==BEGIN==###
        def movewindow(event):
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()
        self.ui.frame_top_main.mouseMoveEvent = movewindow
        ###==MOVE_FRAME==END==###

        ###==SIGNALS==BEGIN==###
        self.ui.btn_close.clicked.connect(lambda: self.close())
        self.ui.btn_minimize.clicked.connect(lambda: self.showMinimized())
        self.ui.btn_bot_logout.clicked.connect(self.buttons)
        self.ui.btn_login_enter.clicked.connect(self.buttons)
        self.ui.btn_home_add.clicked.connect(self.buttons)
        ###==SIGNALS==END==###

        if not os.path.exists(Settings.pathFile):
            LoginFunctions.firstLaunch(self)

        self.show()

    def buttons(self):
        btn = self.sender()
        if btn.objectName() == "btn_login_enter":
            editPass = self.ui.edit_login_pass.text()
            if editPass:
                if " " not in editPass:
                    if self.settings.value("Password") != "Null":
                        if hashlib.sha3_256(editPass.encode()).hexdigest() == self.settings.value("Password"):
                            LoginFunctions.localEnter(self)
                            StorageFunctions.restoreApp(self, editPass)
                        else:
                            self.ui.label_bot_error.setText("Ошибка: Введенный пароль не подходит.")
                    else:
                        self.settings.setValue("Password", hashlib.sha3_256(editPass.encode()).hexdigest())
                        self.ui.edit_login_pass.clear()
                        self.ui.label_bot_error.setText("Успех: Пароль задан.")
                    self.key = editPass
                else:
                    self.ui.label_bot_error.setText("Ошибка: Поле 'Пароль' не может содержать пробелы.")
            else:
                self.ui.label_bot_error.setText("Ошибка: Поле 'Пароль' не может быть пустым.")

        if btn.objectName() == "btn_bot_logout":
            self.key = str
            LoginFunctions.localLogout(self)

        if btn.objectName() == "btn_home_add":
            editApp = self.ui.edit_home_app.text()
            editLogin = self.ui.edit_home_login.text()
            editMail = self.ui.edit_home_mail.text()
            editPass = self.ui.edit_home_pass.text()
            editCom = self.ui.edit_home_comment.toPlainText()
            if editApp and editLogin and editPass:
                if " " not in editLogin:
                    if " " not in editMail:
                        if " " not in editPass:
                            StorageFunctions.addApp(self, self.key, editApp, editLogin, editMail, editPass, editCom)
                            self.ui.label_bot_error.clear()
                            self.ui.label_bot_error.setText("Успех: Запись добавлена.")
                        else:
                            self.ui.label_bot_error.setText("Ошибка: Поле 'Пароль' не может содержать пробелы.")
                    else:
                        self.ui.label_bot_error.setText("Ошибка: Поле 'Почта' не может содержать пробелы.")
                else:
                    self.ui.label_bot_error.setText("Ошибка: Поле 'Логин' не может содержать пробелы.")
            else:
                self.ui.label_bot_error.setText("Ошибка: Поля 'Приложение, Логин, Пароль' не могут быть пустыми.")

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

def exceptHook(exc_type, exc_value, exc_tb):
    print(''.join(traceback.format_exception(exc_type, exc_value, exc_tb)))
    QApplication.quit()

if __name__ == "__main__":
    sys.excepthook = exceptHook
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())