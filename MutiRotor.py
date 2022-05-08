"""
======================
@author:Fandes
@time:2022/4/29:14:35
======================
"""
from websocketserver import MCWebSocketserver
from httpserver import httpserver
from MCuart import MCwin
import sys
import time

import chardet
import serial  # 导入模块
from PyQt5.QtCore import QPoint, QRectF, QMimeData, QObject
from PyQt5.QtCore import QRect, Qt, pyqtSignal, QStandardPaths, QTimer, QSettings, QUrl
from PyQt5.QtGui import QCursor, QBrush
from PyQt5.QtGui import QPixmap, QPainter, QPen, QIcon, QFont, QImage, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QTextEdit, QFileDialog, QMenu, QGroupBox, QSpinBox, \
    QWidget, QComboBox
from PyQt5.QtWidgets import QSlider, QColorDialog
from PyQt5.QtCore import QRect, Qt, QThread, pyqtSignal, QStandardPaths, QTimer, QSettings, QFileInfo, \
    QUrl, QObject, QSize
from PyQt5.QtGui import QPixmap, QPainter, QPen, QIcon, QFont, QImage, QTextCursor, QColor, QDesktopServices, QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QToolTip, QAction, QTextEdit, QLineEdit, \
    QMessageBox, QFileDialog, QMenu, QSystemTrayIcon, QGroupBox, QComboBox, QCheckBox, QSpinBox, QTabWidget, \
    QDoubleSpinBox, QLCDNumber, QScrollArea, QWidget, QToolBox, QRadioButton, QTimeEdit, QListWidget, QDialog, \
    QProgressBar, QTextBrowser
import serial.tools.list_ports



if __name__ == '__main__':
    app = QApplication(sys.argv)
    wsserver = MCWebSocketserver()
    wsserver.start()
    http_Server = httpserver()
    http_Server.start()
    s = MCwin()
    s.show()
    sys.exit(app.exec_())



