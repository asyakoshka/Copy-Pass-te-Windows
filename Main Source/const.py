import os
import sys
import json
import string
import psutil
import random
import sqlite3
import logging
import hashlib
import traceback
from pathlib import Path
from time import time, sleep
from base64 import b64encode, b64decode
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ui_main import Ui_MainWindow

class CONST:
    APPLICATION_NAME = "CopyPasste"
    ORGANIZATION_NAME = "Osborn"

class Settings:
    settings = QSettings(QSettings.IniFormat, QSettings.UserScope, CONST.ORGANIZATION_NAME, CONST.APPLICATION_NAME)
    pathFile = settings.fileName()
    pathDir = os.path.dirname(settings.fileName())
    pathDb = Path(pathDir, "localhost")
    if not os.path.exists(pathDb):
        os.mkdir(pathDb)