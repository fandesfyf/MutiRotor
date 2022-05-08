"""
======================
@author:Fandes
@time:2022/5/2:14:35
======================
"""
import sys
import time

import serial  # 导入模块
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QComboBox, QSpinBox, QWidget, QTabWidget
from MCuart import MCwin, ReconnectThread


class PWM_Widget(QWidget):
    def __init__(self, parent: MCwin):
        super(PWM_Widget, self).__init__()
        self.parent = parent
        self.resize(550, 400)
        self.move(0, 0)

        self.ser = Serial_MD(self)
        self.ser.statesignal.connect(self.setstate)
        self.reconnectthread = ReconnectThread(self,self.ser)
        self.speedchanging = 0  # 不变,1自动加速,2自动减速
        self.pwmdchange = 0  # 0不变,1:+10 2:-10,3停止
        btn1 = QPushButton("加速", self)
        btn1.setGeometry(20, 20, 80, 40)
        btn1.setShortcut("W")
        btn1.clicked.connect(self.speedup)
        btn2 = QPushButton("减速", self)
        btn2.setShortcut("S")
        btn2.setGeometry(20, 80, 80, 40)
        btn2.clicked.connect(self.speeddown)
        btn3 = QPushButton("PWM-10", self)
        btn3.setShortcut("A")
        btn3.setGeometry(120, 20, 80, 40)
        btn3.clicked.connect(self.pwmd)
        btn4 = QPushButton("PWM+10", self)
        btn4.setShortcut("D")
        btn4.setGeometry(120, 80, 80, 40)
        btn4.clicked.connect(self.pwmp)
        btn5 = QPushButton("STOP", self)
        btn5.setShortcut(" ")
        btn5.setGeometry(20, 140, 80, 40)
        btn5.clicked.connect(self.stop)

        self.btl = QComboBox(self)
        self.btl.move(self.width() - 100, 20)
        self.btl.addItems(
            ['1200', '2400', '4800', '9600', '14400', '19200', '38400', '43000', '57600', '76800', '115200',
             '128000', '230400', '256000'])
        self.btl.setCurrentText('57600')
        lb = QLabel("波特率:", self)
        lb.resize(55, 20)
        lb.move(self.btl.x() - lb.width(), self.btl.y())
        # self.copy_type_ss.currentTextChanged.connect(self.setting_save)

        self.comx = QSpinBox(self)
        self.comx.setPrefix('COM')
        self.comx.setMaximum(50)
        ls = self.first_search()
        if len(ls):
            self.comx.setValue(ls[-1])
        else:
            self.comx.setValue(7)
        self.comx.setGeometry(self.btl.x(), self.btl.y() + self.btl.height() + 5, 80, 25)
        self.connectbtn = QPushButton("Connect", self)
        self.connectbtn.setGeometry(lb.x() - 100, self.btl.y(), 80, 25)
        self.connectbtn.clicked.connect(self.ser.connectchange)

        self.state = QLabel(self)
        self.state.setWordWrap(True)
        self.state.setGeometry(self.width() - 320, self.height() - 200, 300, 180)
        self.state.setText("未连接!")
        self.state.setFont(QFont("Timers", 28, QFont.Bold))

        self.reconnectthread.start()

    def first_search(self):
        return [int(i.device.lstrip("COM")) for i in list(serial.tools.list_ports.comports())]

    def setstate(self, s):
        self.state.setText(s)

    def speedup(self):
        if self.speedchanging == 1:
            self.speedchanging = 0
        else:
            self.speedchanging = 1
        self.updatecmd()

    def speeddown(self):
        if self.speedchanging == 2:
            self.speedchanging = 0
        else:
            self.speedchanging = 2
        self.updatecmd()

    def pwmd(self):
        self.pwmdchange = 2
        self.updatecmd()

    def pwmp(self):
        self.pwmdchange = 1
        self.updatecmd()

    def stop(self):
        self.speedchanging = 0
        self.pwmdchange = 3
        self.updatecmd()

    def updatecmd(self):
        print("update>{}|{}<".format(self.speedchanging, self.pwmdchange))
        self.ser.senddata(">{}|{}<\r\n".format(self.speedchanging, self.pwmdchange))
        self.pwmdchange = 0


class Serial_MD(QThread):
    statesignal = pyqtSignal(str)

    def __init__(self, parent:PWM_Widget, port="COM7", bps=57600):
        super(Serial_MD, self).__init__()
        self.parent = parent
        self.connected = False

    def connectchange(self):
        if self.connected:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        print("connecting")
        try:
            self.ser = serial.Serial("com" + str(self.parent.comx.value()), int(self.parent.btl.currentText()),
                                     timeout=6000)
            self.statesignal.emit("连接中")
            self.connected = True
        except:
            e = sys.exc_info()
            print(e, 103)
            self.statesignal.emit(str(e[1]))
        else:
            self.start()
            print("线程开始")

    def disconnect(self):
        try:
            self.connected = False
            self.ser.close()  # 关闭串口
            self.statesignal.emit("已断开")
        except:
            print(sys.exc_info(), 103)
            self.statesignal.emit("断开失败")

    def senddata(self, d):
        try:
            result = self.ser.write(d.encode("gbk"))
            print("写总字节数:", result)
        except:
            print(sys.exc_info(), 136)

    def run(self) -> None:
        st = time.time()
        try:
            totals = ""
            while self.ser.isOpen():
                time.sleep(0.05)
                if self.ser.in_waiting:
                    st = time.time()
                    s = self.ser.read(self.ser.in_waiting)
                    try:
                        s = s.decode('ascii')
                    except UnicodeDecodeError:
                        s = s.decode('gbk', "ignore")
                    totals += s
                    print('a' in totals)
                    a = totals.rfind(">")
                    b = totals.rfind("<")
                    if b <= 1 or a == 0:
                        time.sleep(0.05)
                        continue
                    if a > b:
                        a = totals[:b].rfind(">")
                    pwm = totals[a + 1:b]
                    totals = totals[b + 1:]
                    print("收到数据：{} || {}".format(totals, pwm))
                    if pwm.isalnum():
                        self.statesignal.emit("当前PWM:{}".format(pwm))
                    else:
                        self.statesignal.emit("无效数据...".format(pwm))
                if time.time() - st > 1:
                    self.statesignal.emit("已连接,等待中...")
                    time.sleep(0.1)
        except:
            print(sys.exc_info(), "线程内错误")
        finally:
            print("线程结束")
            try:
                self.disconnect()
            except:
                print(sys.exc_info(), 159)
