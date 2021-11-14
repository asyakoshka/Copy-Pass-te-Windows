from const import *


class UIFunctions:
    def __init__(self, SELF, UI, SF, AH, USB):
        self.ui = UI
        self.win = SELF
        self.SF = SF
        self.AH = AH
        self.USB = USB

    def uiDefinitions(self):
        self.ui.cmb_auth_usb.hide()

        self.win.setWindowFlags(Qt.FramelessWindowHint)
        self.win.setAttribute(Qt.WA_TranslucentBackground)
        def moveWindow(event):
            if event.buttons() == Qt.LeftButton:
                self.win.move(self.win.pos() + event.globalPos() - self.win.dragPos)
                self.win.dragPos = event.globalPos()
                event.accept()
        self.ui.frame_top_main.mouseMoveEvent = moveWindow

    def signalsConnect(self):
        self.USB.sigGetUsb.connect(self.AH.USBGet, Qt.QueuedConnection)
        self.ui.btn_minimize.clicked.connect(lambda: self.win.showMinimized())
        self.ui.btn_close.clicked.connect(lambda: self.win.close())
        self.ui.btn_home_add.clicked.connect(self.SF.addData)


class OtherFunctions:
    def __init__(self, SELF, UI):
        self.win = SELF
        self.ui = UI

    def random(self, length=16):
        alpha = string.ascii_letters + string.digits
        return ''.join(random.sample(alpha, length))

    def SHA256(self, data):
        return hashlib.sha3_256(data.encode()).hexdigest()

    def SHA512(self, data):
        return hashlib.sha3_512(data.encode()).hexdigest()

    def encryptDataAES(self, data, password, n=2 ** 14, r=8, salt=16):
        """Описание параметров функции:

         - Text = текст для шифрования
         - Password = ваш пароль для защиты текста
         - n = фактор загрузки CPU/RAM
         - r = размер блока
         - p = фактор параллелизма (Половина от количества ядер)
         - salt = случайный набор байтов для усиления пароля
        """
        p = int(psutil.cpu_count() / 2)
        salt = get_random_bytes(salt)
        private_key = hashlib.scrypt(password.encode(), salt=salt, n=n, r=r, p=p, maxmem=128 * r * (n + p + 2), dklen=32)
        cipher_config = AES.new(private_key, AES.MODE_GCM)
        cipher_text, tag = cipher_config.encrypt_and_digest(bytes(data, 'utf-8'))
        return '.'.join([b64encode(cipher_text).decode('utf-8'), b64encode(salt).decode('utf-8'),
                         b64encode(cipher_config.nonce).decode('utf-8'), b64encode(tag).decode('utf-8')])

    def decryptDataAES(self, data, password, n=2 ** 14, r=8):
        p = int(psutil.cpu_count() / 2)
        data = data.split('.')
        private_key = hashlib.scrypt(password.encode(), salt=b64decode(data[1]), n=n, r=r, p=p, maxmem=128 * r * (n + p + 2), dklen=32)
        cipher = AES.new(private_key, AES.MODE_GCM, nonce=b64decode(data[2]))
        decrypted = cipher.decrypt_and_verify(b64decode(data[0]), b64decode(data[3]))
        return decrypted.decode('utf-8')

    def encryptFileAES(self, filename, password, n=2 ** 14, r=8, salt=16):
        with open(filename, 'r') as fileData:
            data = fileData.read()
        with open(filename, 'w') as fileEncData:
            fileEncData.write(self.encryptDataAES(data, password, n, r, salt))

    def decryptFileAES(self, filename, password, n=2 ** 14, r=8):
        with open(filename, 'r') as fileData:
            data = fileData.read()
        with open(filename, 'w') as fileDecData:
            fileDecData.write(self.decryptDataAES(data, password, n, r))

    def getAverageEncryptAES(self, cycle=10, n=2 ** 14, r=8, salt=16):
        if not salt % 8:
            randData = self.random()
            randPassword = self.random()
            all_time = []
            for i in range(cycle):
                start_time = time()
                self.encryptDataAES(randData, randPassword, n=n, r=r, salt=salt)
                end_time = time() - start_time
                all_time.append(end_time)
            return sum(all_time) / len(all_time)
        else:
            raise ValueError("Salt должна быть кратна 8")


class Auth:
    def __init__(self, SELF, UI, CF, OF, SF, USB):
        self.win = SELF
        self.ui = UI
        self.CF = CF
        self.OF = OF
        self.SF = SF
        self.USB = USB

    def USBGet(self, drives):
        if not drives:
            self.ui.cmb_auth_usb.clear()
            self.ui.cmb_auth_usb.addItem("Устройства не найдены")
        else:
            self.ui.cmb_auth_usb.clear()
            for drive in drives:
                self.ui.cmb_auth_usb.addItem(drive[0])

    def authStart(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_auth)
        self.CF.settings.beginGroup("Authentication")
        if self.CF.settings.value("Password") or self.CF.settings.value("USBPassword"):
            self.ui.btn_auth_create.setText("Войти")
            self.ui.edit_auth_rPass.hide()
            self.ui.cmb_auth_change.hide()
            if self.CF.settings.value("USBPassword"):
                self.ui.cmb_auth_change.setCurrentIndex(1)
                self.USB.start()
                self.ui.edit_auth_pass.hide()
                self.ui.cmb_auth_usb.show()
        self.CF.settings.endGroup()

        def loginButton():
            self.CF.settings.beginGroup("Authentication")
            if self.ui.cmb_auth_change.currentIndex() == 0:
                editPass = self.ui.edit_auth_pass.text().replace(" ", "")
                encEditPass = self.OF.SHA512(editPass)
                if self.CF.settings.value("Password"):
                    if editPass:
                        if encEditPass == self.CF.settings.value("Password"):
                            self.SF.loadData(editPass)
                            self.ui.stackedWidget.setCurrentWidget(self.ui.page_home)
                            self.ui.label_bot_name.setText("Username: localhost")
                            self.ui.btn_bot_logout.setEnabled(True)
                            self.ui.edit_auth_pass.clear()
                            self.ui.edit_auth_rPass.clear()
                            self.ui.label_bot_error.clear()
                        else:
                            self.ui.label_bot_error.setText("Ошибка: Введенный пароль не подходит.")
                    else:
                        self.ui.label_bot_error.setText("Ошибка: Поле 'Пароль' не может быть пустым.")
                else:
                    editRPass = self.ui.edit_auth_rPass.text().replace(" ", "")
                    if editPass and editRPass:
                        if len(editPass) > 5:
                            if editPass == editRPass:
                                self.ui.label_bot_error.setText(None)
                                self.CF.settings.setValue("Password", encEditPass)
                                self.ui.label_bot_error.setText("Успех: Пароль задан.")
                                self.ui.btn_auth_create.setText("Войти")
                                self.ui.cmb_auth_change.hide()
                                self.ui.edit_auth_rPass.hide()
                                self.ui.edit_auth_pass.clear()
                                self.ui.edit_auth_rPass.clear()
                            else:
                                self.ui.label_bot_error.setText("Ошибка: 'Пароли' не совпадают.")
                        else:
                            self.ui.label_bot_error.setText("Ошибка: 'Пароль' слишком короткий")
                    else:
                        self.ui.label_bot_error.setText("Ошибка: Поле 'Пароль' не может быть пустым.")
            else:
                for drive in self.USB.drivesData:
                    if drive[0].startswith(self.ui.cmb_auth_usb.itemText(self.ui.cmb_auth_usb.currentIndex())):
                        encUSBPass = self.OF.SHA512(drive[1])
                        if self.CF.settings.value("USBPassword"):
                            if encUSBPass == self.CF.settings.value("USBPassword"):
                                self.USB.terminate()
                                self.SF.loadData(drive[1])
                                self.ui.stackedWidget.setCurrentWidget(self.ui.page_home)
                                self.ui.label_bot_name.setText("Username: localhost")
                                self.ui.btn_bot_logout.setEnabled(True)
                                self.ui.label_bot_error.clear()
                            else:
                                self.ui.label_bot_error.setText("Ошибка: Съемный носитель не подходит.")
                        else:
                            self.ui.label_bot_error.setText(None)
                            self.CF.settings.setValue("USBPassword", encUSBPass)
                            self.ui.label_bot_error.setText("Успех: Пароль задан.")
                            self.ui.btn_auth_create.setText("Войти")
                            self.ui.cmb_auth_change.hide()
            self.CF.settings.endGroup()

        def USBAccess():
            if self.ui.cmb_auth_change.currentIndex() == 0:
                self.USB.terminate()
                self.ui.cmb_auth_usb.hide()
                self.ui.edit_auth_pass.show()
                self.ui.edit_auth_rPass.show()
                self.ui.label_bot_error.clear()
            else:
                self.USB.start()
                self.ui.cmb_auth_usb.show()
                self.ui.edit_auth_pass.hide()
                self.ui.edit_auth_rPass.hide()
                self.ui.edit_auth_pass.clear()
                self.ui.edit_auth_rPass.clear()
                self.ui.label_bot_error.clear()

        def logoutButton():
            # Page Home
            self.ui.edit_home_app.clear()
            self.ui.edit_home_login.clear()
            self.ui.edit_home_mail.clear()
            self.ui.edit_home_pass.clear()
            self.ui.edit_home_comment.clear()
            self.ui.list_app.clear()
            # Page Login
            self.ui.edit_auth_pass.clear()
            self.ui.label_bot_name.clear()
            self.ui.label_bot_error.clear()
            self.ui.btn_bot_logout.setEnabled(False)
            # Load page
            self.CF.settings.beginGroup("Authentication")
            if self.CF.settings.value("USBPassword"):
                self.USB.start()
            self.CF.settings.endGroup()
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_auth)
        self.ui.btn_auth_create.clicked.connect(loginButton)
        self.ui.cmb_auth_change.currentIndexChanged.connect(USBAccess)
        self.ui.btn_bot_logout.clicked.connect(logoutButton)


class ConfigFunctions:
    def __init__(self, SELF, UI, OF):
        self.win = SELF
        self.ui = UI
        self.OF = OF
        self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope,
                                  CONST.ORGANIZATION_NAME, CONST.APPLICATION_NAME)
        self.con = sqlite3.connect(Path(os.path.dirname(self.settings.fileName()), "CopyPassTe.db"),
                                   check_same_thread=False)
        self.con.cursor().execute("CREATE TABLE IF NOT EXISTS 'Accounts' "
                                  "('ID' INTEGER PRIMARY KEY AUTOINCREMENT, "
                                  "'App' TEXT, 'Login' TEXT, 'Password' TEXT, "
                                  "'Mail' TEXT, 'Comment' TEXT)")


class StorageFunctions:
    def __init__(self, SELF, UI, OF, CF):
        self.win = SELF
        self.ui = UI
        self.OF = OF
        self.CF = CF

    def loadData(self, key):
        print(os.path.dirname(self.CF.settings.fileName()))

    def addData(self):
        editApp = self.ui.edit_home_app.text()
        editLogin = self.ui.edit_home_login.text().replace(" ", "")
        editPass = self.ui.edit_home_pass.text().replace(" ", "")
        editMail = self.ui.edit_home_mail.text().replace(" ", "")
        editCom = self.ui.edit_home_comment.toPlainText()
        if editApp and editLogin and editPass:
            self.CF.con.cursor().execute(f"INSERT INTO 'Accounts' ('ID','App','Login','Password','Mail','Comment') "
                                         f"VALUES (NULL, '{editApp}','{editLogin}','{editPass}','{editMail}','{editCom}')")
            self.CF.con.commit()

            self.ui.list_app.addItem(editApp)

            self.ui.label_bot_error.setText("Успех: Запись добавлена.")
        else:
            self.ui.label_bot_error.setText("Ошибка: Поля 'Приложение, Логин, Пароль' не могут быть пустыми.")


class USBFunctions(QThread):
    sigGetUsb = pyqtSignal(list)

    def __init__(self):
        QThread.__init__(self)
        self.drivesData = None

    def run(self):
        old_drive = list
        while True:
            print("as")
            try:
                drive = list([f"Съемный диск {i}", str(GetVolumeInformation(i)[1]) + GetVolumeInformation(i)[4]]
                             for i in GetLogicalDriveStrings().split('\000')[:-1] if GetDriveType(i) == 2)
            except:
                drive = old_drive
            if drive != old_drive:
                old_drive = drive
                self.sigGetUsb.emit(drive)
                self.drivesData = drive
            sleep(1)