"""
======================
@author:Fandes
@time:2022/1/2:14:53
======================
"""
import sys
import time
import math
import serial  # 导入模块
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QComboBox, QSpinBox, QWidget, QTabWidget
from pymavlink import mavutil


class MCwin(QWidget):  # 随便设置的一个ui,
    closesignal=pyqtSignal()
    def __init__(self):
        super(MCwin, self).__init__()
        from pwmtest import PWM_Widget
        self.tab = QTabWidget(self)
        self.pwmtab = PWM_Widget(self)
        self.mavcontroller = Mavlink_widget(self)
        self.tab.addTab(self.mavcontroller, "Mavlink测试")
        self.tab.addTab(self.pwmtab, 'PWM测试')
        self.setWindowTitle("多旋翼水空两栖无人机控制界面")
        self.resize(600, 500)
        self.tab.setGeometry(5, 2, 590, 496)
        self.closesignal.connect(self.mavcontroller.mav.disconnect)

    def show(self) -> None:
        super(MCwin, self).show()
        print("ss show")

    def closeEvent(self, e):
        self.closesignal.emit()
        super(MCwin, self).closeEvent(e)

class ReconnectThread(QThread):
    def __init__(self, parent, connection):
        super(ReconnectThread, self).__init__()
        self.parent = parent
        self.connection = connection
        self.oldls = self.parent.first_search()

    def run(self) -> None:
        print("reconnectthread start")
        while True:
            if not self.parent.isVisible():
                time.sleep(0.1)
                continue
            if self.connection.connected:
                time.sleep(0.5)
                continue
            newls = self.parent.first_search()
            if self.oldls != newls:
                addport = [i for i in newls if i not in self.oldls]
                print(addport)
                if len(addport):
                    self.parent.comx.setValue(addport[0])
                    time.sleep(0.5)
                    self.connection.connect()
                self.oldls = newls
            time.sleep(0.1)


class Mavlink_widget(QWidget):
    def __init__(self, parent: MCwin):
        super(Mavlink_widget, self).__init__()
        self.parent = parent
        self.resize(550, 400)
        self.move(0, 0)
        self.mav = Mavlink_MD(self)
        self.mav.statesignal.connect(self.setstate)
        self.mav.attitudesignal.connect(self.update_attitude)
        self.mav.possignal.connect(self.update_pos)
        self.mav.target_back_signal.connect(self.update_thrust)
        self.mav.sys_status_signal.connect(self.update_sys_status)
        self.bodystatus = {"x": 0, "y": 0, "z": 0, "vx": 0, "vy": 0, "vz": 0, "roll": 0, "pitch": 0, "yaw": 0, "rs": 0,
                           "ps": 0, "ys": 0, "battery": 100, 'thrust': 0, "status": "unknown", "mode": "unknown"}
        self.mav.batterysignal.connect(self.update_battery)
        self.reconnectthread = ReconnectThread(self, self.mav)
        self.speedchanging = 0  # 不变,1自动加速,2自动减速
        self.pwmdchange = 0  # 0不变,1:+10 2:-10,3停止
        btn1 = QPushButton("解锁", self)
        btn1.setGeometry(20, 20, 80, 40)
        # btn1.setShortcut("v")
        btn1.clicked.connect(self.arm)
        btn2 = QPushButton("上锁", self)
        # btn2.setShortcut("f")
        btn2.setGeometry(20, 80, 80, 40)
        btn2.clicked.connect(self.disarm)
        btn3 = QPushButton("起飞", self)
        # btn3.setShortcut("L")
        btn3.setGeometry(120, 20, 80, 40)
        btn3.clicked.connect(self.takeoff)
        btn4 = QPushButton("降落", self)
        # btn4.setShortcut("D")
        btn4.setGeometry(120, 80, 80, 40)
        btn4.clicked.connect(self.land)
        btn5 = QPushButton("send", self)
        # btn5.setShortcut(" ")
        btn5.setGeometry(20, 140, 80, 40)
        btn5.clicked.connect(self.sendpos)

        btn51 = QPushButton("offboard", self)
        # btn5.setShortcut(" ")
        btn51.setGeometry(120, 140, 80, 40)
        btn51.clicked.connect(self.in_offboard)

        btn6 = QPushButton("stabilize", self)
        # btn5.setShortcut(" ")
        btn6.setGeometry(200, 140, 80, 40)
        btn6.clicked.connect(self.switch_mode)

        self.sb = QSpinBox(self)
        self.sb.setGeometry(200, 80, 80, 40)
        self.sb.setMinimum(-10)
        self.sb.setMaximum(10)
        self.sb.setValue(-2)

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
        self.connectbtn.clicked.connect(self.mav.connectchange)

        self.state = QLabel(self)
        self.state.setWordWrap(True)
        self.state.setGeometry(5, self.height() - 200, 540, 200)
        self.state.setText("未连接!")
        self.state.setFont(QFont("Timers", 15, QFont.Bold))

        self.reconnectthread.start()

    def first_search(self):
        return [int(i.device.lstrip("COM")) for i in list(serial.tools.list_ports.comports())]

    def setstate(self, s):
        id = ['{:>4}:{:>6.2f} ', '{:>5}:{:>6.2f} ', '{:>3}:{:>6.2f}\n',
              '{:>4}:{:>6.3f} ', '{:>5}:{:>6.3f} ', '{:>3}:{:>6.3f}\n',
              '{:>4}:{:>6.2f} ', '{:>5}:{:>6.2f} ', '{:>3}:{:>6.2f}\n',
              '{:>4}:{:>6.3f} ', '{:>5}:{:>6.3f} ', '{:>3}:{:>6.3f}\n',
              "{:>6}:{:>3.1f}% ", '{:>5}:{:<6.3f}\n',
              "{:>5}:{:<5} ", "{:>5}:{:<10}"]
        status = "".join([i.format(k, v) for k, v, i in
                          zip(self.bodystatus.keys(), self.bodystatus.values(), id)])
        self.state.setText(s + status)

    def update_attitude(self, r, p, y, rs, ps, ys):
        self.bodystatus["roll"] = r
        self.bodystatus["pitch"] = p
        self.bodystatus["yaw"] = y
        self.bodystatus["rs"] = rs
        self.bodystatus["ps"] = ps
        self.bodystatus["ys"] = ys

    def update_thrust(self, t, rr, pr, yr):
        self.bodystatus["thrust"] = t

    def update_sys_status(self, syss, mode):
        self.bodystatus["status"] = syss
        self.bodystatus["mode"] = mode

    def update_pos(self, x, y, z, vx, vy, vz):
        self.bodystatus["x"] = x
        self.bodystatus["y"] = y
        self.bodystatus["z"] = z
        self.bodystatus["vx"] = vx
        self.bodystatus["vy"] = vy
        self.bodystatus["vz"] = vz

    def update_battery(self, s):
        self.bodystatus["battery"] = s

    def arm(self):  # 1
        self.mav.connection.mav.custom_cmd_send(self.mav.timestamp + 200, 1, 0, 0, 0, 0, 0, "0".encode())

        print("mav send")

    def disarm(self):  # 2
        self.mav.connection.mav.custom_cmd_send(self.mav.timestamp + 200, 2, 0, 0, 0, 0, 0, "0".encode())
        print("cmd send")

    def switch_mode(self):  # 4
        # 参数1为2起飞,1降落,其他为自稳
        self.mav.connection.mav.custom_cmd_send(self.mav.timestamp + 200, 3, 0, 0, 0, 0, 0, "0".encode())

    def takeoff(self):  # 4
        self.mav.connection.mav.custom_cmd_send(self.mav.timestamp + 200, 3, 2, 0, 0, 0, 0, "0".encode())

        # self.pwmdchange = 2
        # self.updatecmd()

    def land(self):  # 3
        self.mav.connection.mav.custom_cmd_send(self.mav.timestamp + 200, 3, 1, 0, 0, 0, 0, "0".encode())

        # self.pwmdchange = 1
        # self.updatecmd()

    def sendpos(self):
        self.mav.pos_control(0, 0, -1)
        # self.speedchanging = 0
        # self.pwmdchange = 3
        # self.updatecmd()

    def in_offboard(self):
        # self.mav.in_offboard = ~self.mav.in_offboard
        self.mav.connection.mav.custom_cmd_send(self.mav.timestamp, 0, 0, 0, 0, 0, 0, "0".encode())
        # self.mav.pos_control(0, 0, -2)

    def updatecmd(self):
        print("update>{}|{}<".format(self.speedchanging, self.pwmdchange))
        # self.ser.senddata(">{}|{}<\r\n".format(self.speedchanging, self.pwmdchange))
        self.pwmdchange = 0



class Mavlink_MD(QThread):
    statesignal = pyqtSignal(str)
    batterysignal = pyqtSignal(int)
    attitudesignal = pyqtSignal(float, float, float, float, float, float)
    possignal = pyqtSignal(float, float, float, float, float, float)
    target_back_signal = pyqtSignal(float, float, float, float)
    sys_status_signal = pyqtSignal(str, str)

    def __init__(self, parent: Mavlink_widget, com='com3'):
        super(Mavlink_MD, self).__init__()
        self.parent = parent
        self.connected = False
        self.in_offboard = False
        self.com = com
        self.sendflag = {"pos": [], }
        self.timestamp = 0
        self.inittime = 0
        self.connection = None

    def handle_cmd(self, t, r, p, y, d, mode):
        print("handle", t, r, p, y, d, mode)
        if mode == 1:
            self.vcc_control(t, r, p)
        else:
            self.attitude_control(r, p, y, t)

    def connectchange(self):
        if self.connected:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        print("connecting mav")
        try:
            self.statesignal.emit("mavlink 连接中...")
            self.connection = mavutil.mavlink_connection("com" + str(self.parent.comx.value()),
                                                         baud=int(self.parent.btl.currentText()), force_connected=True)
            self.connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
                                               mavutil.mavlink.MAV_AUTOPILOT_INVALID, 1, 0, 0)

            self.statesignal.emit("Mavlink已连接,等待中...")
            self.connected = True
        except:
            e = sys.exc_info()
            print(e, 103)
            self.statesignal.emit(str(e[1]))
        else:
            self.start()
            print("线程开始")

    def disconnect(self):
        print("disconnecting mav")
        try:
            self.connected = False
            self.connection.close()  # 关闭串口
            self.statesignal.emit("已断开")
        except:
            print(sys.exc_info(), 103)
            self.statesignal.emit("断开失败")
            self.connection = None

    def run(self) -> None:
        self.connected = True
        print("mavlink start")
        send_thread = Commen_Thread(self.listen_to_send)
        send_thread.start()
        self.inittime = 0
        try:
            while self.connected:
                msg = self.connection.recv_match(blocking=True)
                if msg:
                    datas = msg.to_dict()
                    # print(datas)
                    if "timestamp" in datas or "time_boot_ms" in datas or "time_usec" in datas:
                        try:
                            self.timestamp = datas["timestamp"]
                        except:
                            try:
                                self.timestamp = datas["time_boot_ms"] * 1000
                            except:
                                self.timestamp = datas["time_usec"]
                        if self.inittime == 0 or self.inittime > self.timestamp:
                            self.inittime = self.timestamp
                        status = "time:{:.2f}\n".format((self.timestamp - self.inittime) / 1000000)
                        self.statesignal.emit(status)

                    if datas["mavpackettype"] == "SYS_STATUS":
                        self.batterysignal.emit(datas["battery_remaining"])
                    elif datas["mavpackettype"] == "ODOMETRY":
                        self.possignal.emit(datas['x'], datas['y'], datas['z'], datas['vx'], datas['vy'], datas['vz'])
                    elif datas["mavpackettype"] == "ATTITUDE":
                        self.attitudesignal.emit(math.degrees(datas['roll']), math.degrees(datas['pitch']),
                                                 math.degrees(datas['yaw']), math.degrees(datas['rollspeed']),
                                                 math.degrees(datas['pitchspeed']), math.degrees(datas['yawspeed']))
                    elif datas["mavpackettype"] == "ATTITUDE_TARGET":
                        self.target_back_signal.emit(datas['thrust'], math.degrees(datas['body_roll_rate']),
                                                     math.degrees(datas['body_pitch_rate']),
                                                     math.degrees(datas['body_yaw_rate']))
                    # elif datas["mavpackettype"] == "DISTANCE_SENSOR":
                    #     print("DISTANCE_SENSOR:", datas["current_distance"])
                    elif datas["mavpackettype"] == "HEARTBEAT":
                        system_status = {3: "未解锁", 4: "flying", 5: "flying2"}
                        custom_mode = {100925440: "Land", 33816576: "Takeoff", 393216: "Offboard", 458752: "Stabilized",
                                       196608: "Position"}
                        "system_status 表示系统状态 为3 即未解锁disarm,为4则已解锁或飞行中"
                        "custom_mode 表示模式,100925440 降落,33816576 起飞,393216 offboard,458752 自稳 ,196608 定点"
                        # print("SYSSTATUS:",datas["system_status"],datas["custom_mode"])
                        self.sys_status_signal.emit(system_status[datas["system_status"]] if datas[
                                                                                                 "system_status"] in system_status else "unknown",
                                                    custom_mode[datas["custom_mode"]] if datas[
                                                                                             "custom_mode"] in custom_mode else "unknown")
                    # if datas["mavpackettype"] in ["CUSTOM_CMD"]:
                    #     print(datas)
                    # if datas["mavpackettype"] not in ['BAD_DATA', 'UNKNOWN_8', 'SYS_STATUS', 'ATTITUDE']:
                    #     print(datas)
                    # self.connection.mav.set_position_target_local_ned_send(datas["timestamp"], 0, 0, 0, 0, 0, 0, -5,
                    #                                                        0, 0, 0, 0, 0, 0, 0, 0, 0)

                    # if mavutil.all_printable(msg):
                    #     print()

                    continue
                time.sleep(0.02)
            self.connection.close()
        except:
            print(sys.exc_info(), 263)
            self.statesignal.emit("异常退出{}".format(sys.exc_info()[1]))
        self.connected = False

        print("mavlink thread end")

    def pos_control(self, x=0.0, y=0.0, z=0.0, vcc=None):
        # MAV_FRAME_BODY_NED只有速度加速度控制
        if not self.connection:return
        if vcc is None:
            vcc = [0.0, 0.0, 0.0]
        self.connection.mav.set_position_target_local_ned_send(0, 0, 0,
                                                               # mavutil.mavlink.MAV_FRAME_BODY_NED,
                                                               mavutil.mavlink.MAV_FRAME_LOCAL_NED,
                                                               # 0b0000111111111000,
                                                               0b0000111111000000 if vcc else 0b0000111111111000,
                                                               x, y, z,
                                                               vcc[0], vcc[1], vcc[2],
                                                               0, 0, 0,
                                                               0, 0)
        print("set pos x:{} y:{} z:{}".format(x, y, z))

    def vcc_control(self, vx, vy, vz):
        if not self.connection:return

        self.connection.mav.set_position_target_local_ned_send(0, 0, 0,
                                                               # mavutil.mavlink.MAV_FRAME_BODY_NED,
                                                               mavutil.mavlink.MAV_FRAME_BODY_NED,
                                                               # 0b0000111111111000,
                                                               0b0000111111000111,
                                                               0, 0, 0,
                                                               vx, vy, vz,
                                                               0, 0, 0,
                                                               0, 0)
        print("set vcc vx:{} vy:{} vz:{}".format(vx, vy, vz))

    def attitude_control(self, roll, pitch, yaw, th):
        if not self.connection:return

        # self.connection.mav.set_position_target_local_ned_send(0, 0, 0,
        #                                                        # mavutil.mavlink.MAV_FRAME_BODY_NED,
        #                                                        mavutil.mavlink.MAV_FRAME_BODY_NED,
        #                                                        # 0b0000111111111000,
        #                                                        0b0000111111000111,
        #                                                        0, 0, 0,
        #                                                        vx, vy, vz,
        #                                                        0, 0, 0,
        #                                                        0, 0)
        print("set attitude r:{} p:{} y:{} th:{}".format(roll, pitch, yaw, th))

    def listen_to_send(self):
        i = 0
        while self.connected:
            i += 1
            if i % 10 == 0:
                self.connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
                                                   mavutil.mavlink.MAV_AUTOPILOT_PX4, 1, 0, 0)
            time.sleep(0.01)


class Commen_Thread(QThread):
    def __init__(self, action, *args):
        super(QThread, self).__init__()
        self.action = action
        self.args = args

    def run(self):
        print('start_thread params:{}'.format(self.args))
        if self.args:
            print(self.args)
            if len(self.args) == 1:
                self.action(self.args[0])
            elif len(self.args) == 2:
                self.action(self.args[0], self.args[1])
            elif len(self.args) == 3:
                self.action(self.args[0], self.args[1], self.args[2])
            elif len(self.args) == 4:
                self.action(self.args[0], self.args[1], self.args[2], self.args[3])
        else:
            self.action()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    s = MCwin()
    s.show()
    # mav = Mavlink_MD("COM6")
    # mav.start()
    sys.exit(app.exec_())
