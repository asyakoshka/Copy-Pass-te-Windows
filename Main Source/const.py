import os
import os.path
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
from win32file import GetDriveType
from win32api import GetLogicalDriveStrings, GetVolumeInformation
from time import time, sleep
from base64 import b64encode, b64decode
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ui_main import Ui_MainWindow

class CONST:
    APPLICATION_NAME = "CopyPassTe"
    ORGANIZATION_NAME = "Osborn"