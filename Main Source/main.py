from func import *
# 54
class MainWindow(QMainWindow):
    def __init__(self):
        ###==SETUP==BEGIN==###
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.USB = USBFunctions()

        self.OF = OtherFunctions(self, self.ui)
        self.CF = ConfigFunctions(self, self.ui, self.OF)
        self.SF = StorageFunctions(self, self.ui, self.OF, self.CF)
        self.AH = Auth(self, self.ui, self.CF, self.OF, self.SF, self.USB)
        self.UF = UIFunctions(self, self.ui, self.SF, self.AH, self.USB)

        self.UF.signalsConnect()
        self.UF.uiDefinitions()
        self.AH.authStart()
        ###==SETUP==END==###
        self.show()

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