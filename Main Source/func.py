from const import *

def rand(length=16):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))

class LoginFunctions(Ui_MainWindow):
    def __init__(self):
        self.ui = self

    def firstLaunch(self):
        Settings.settings.setValue("Password", "Null")

    def localEnter(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_home)
        self.ui.label_bot_name.setText("Username: localhost")
        self.ui.btn_bot_logout.setEnabled(True)
        self.ui.edit_login_pass.clear()
        self.ui.label_bot_error.clear()

    def localLogout(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_login)
        # Page Home
        self.ui.edit_home_app.clear()
        self.ui.edit_home_login.clear()
        self.ui.edit_home_mail.clear()
        self.ui.edit_home_pass.clear()
        self.ui.edit_home_comment.clear()
        self.ui.list_app.clear()
        # Page Login
        self.ui.edit_login_pass.clear()
        self.ui.label_bot_name.clear()
        self.ui.label_bot_error.clear()
        self.ui.btn_bot_logout.setEnabled(False)

class StorageFunctions(Ui_MainWindow):
    def __init__(self):
        self.ui = self
        self.encFunc = EncryptFunctions()

    def addApp(self, key, app=None, login=None, mail=None, passw=None, comment=None):
        accDir = Path(Settings.pathDb, 'Accounts.cpt')
        formAcc = {
                "App": b64encode(app.encode()).decode('utf-8'),
                "Login": b64encode(login.encode()).decode('utf-8'),
                "Mail": b64encode(mail.encode()).decode('utf-8'),
                "Password": b64encode(passw.encode()).decode('utf-8'),
                "Comment": b64encode(comment.encode()).decode('utf-8')
        }
        file = None
        if os.path.exists(accDir):
            with open(accDir) as oldFile:
                file = json.loads(self.encFunc.decryptDataAES(oldFile.read(), key))
            file.append(formAcc)
            with open(accDir, "w") as newFile:
                newFile.write(self.encFunc.encryptDataAES(json.dumps(file), key))
        else:
            with open(accDir, "w") as newFile:
                newFile.write(self.encFunc.encryptDataAES(json.dumps([formAcc]), key))
        file = None
        self.ui.list_app.addItem(app)

    def restoreApp(self, key):
        accDir = Path(Settings.pathDb, 'Accounts.cpt')
        if os.path.exists(accDir):
            with open(accDir) as oldFile:
                file = json.loads(self.encFunc.decryptDataAES(oldFile.read(), key))
                for i in file:
                    self.ui.list_app.addItem(b64decode(i["App"]).decode('utf-8'))


class EncryptFunctions:
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
            randData = rand()
            randPassword = rand()
            all_time = []
            for i in range(cycle):
                start_time = time()
                self.encryptDataAES(randData, randPassword, n=n, r=r, salt=salt)
                end_time = time() - start_time
                all_time.append(end_time)
            return sum(all_time) / len(all_time)
        else:
            raise ValueError("Salt должна быть кратна 8")