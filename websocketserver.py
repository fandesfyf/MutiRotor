"""
======================
@author:Fandes
@time:2022/4/28:19:28
======================
"""
import asyncio
import json
import os
import sys
import threading
import time
from PyQt5.QtCore import QRect, Qt, QThread, pyqtSignal, QStandardPaths, QTimer, QSettings, QFileInfo, \
    QUrl, QObject, QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QToolTip, QAction, QTextEdit, QLineEdit, \
    QMessageBox, QFileDialog, QMenu, QSystemTrayIcon, QGroupBox, QComboBox, QCheckBox, QSpinBox, QTabWidget, \
    QDoubleSpinBox, QLCDNumber, QScrollArea, QWidget, QToolBox, QRadioButton, QTimeEdit, QListWidget, QDialog, \
    QProgressBar, QTextBrowser
import websockets
from httpserver import httpserver as Httpserver


# 这个是用于测试的服务端程序,没有接入ros,用于测试连接
class MCWebSocketserver(QThread):
    ws_cmd_signal = pyqtSignal(float, float, float, float, float, int)

    def __init__(self, host="", port=8787):
        super(MCWebSocketserver, self).__init__()
        self.host, self.port = host, port
        self.set_point = {"t": 0, "r": 0, "p": 0, "y": 0, "d": 0, "mode": 1}
        self.send_date = {"update": 0}

    def update_status(self, x, y, z, status):
        self.send_date = {"update": True, "x": x, "y": y, "z": z, "status": status}

    async def requestcallback(self, websocket, path):
        print("request path:", path)
        if path == "/control":
            print("control speed")
            try:
                task = asyncio.get_event_loop().create_task(self.speedcontrol(websocket))
                task2 = asyncio.get_event_loop().create_task(self.heartbeat(websocket))
                sendstatus = asyncio.get_event_loop().create_task(self.sendstatus(websocket))
                await task
                await task2
                await sendstatus
            except:
                print(sys.exc_info(), 31)


        else:
            print("unknown request")
            await websocket.send("unknown request")
        print("end")

    def run(self):
        # asyncio.get_event_loop().run_until_complete(self.websockets_server)
        self.new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.new_loop)
        self.websockets_server = websockets.serve(self.requestcallback, self.host, self.port, ping_interval=0.1,
                                                  ping_timeout=10, timeout=10)
        self.new_loop.run_until_complete(self.websockets_server)
        print("websocket server started!")
        self.new_loop.run_forever()
        print("websocket server exited!")

    def stop(self):
        self.new_loop.stop()

    # 接收客户端消息并处理
    async def speedcontrol(self,
                           websocket: websockets.WebSocketServerProtocol):  # websockets.server.WebSocketServerProtocol
        while True:
            recv_text = await websocket.recv()
            try:
                # print("rec:", recv_text)
                a = json.loads(recv_text)
                self.ws_cmd_signal.emit(round(a["t"], 2), round(a["r"], 2), round(a["p"], 2), round(a["y"], 2),
                                        round(a["d"], 2), a["mode"])
                self.set_point = a
            except:
                print(sys.exc_info(), 60)

    async def sendstatus(self, websocket):
        while True:
            try:
                if self.send_date["update"]:
                    await websocket.send(json.dumps(self.send_date))
                    self.send_date["update"] = False
                else:
                    await asyncio.sleep(0.02)
            except:
                print(sys.exc_info(), 87)
                break

    async def heartbeat(self, websocket):
        while True:
            # print("heartbeat")
            try:
                await websocket.send("0")
                await asyncio.sleep(0.5)
            except:
                print(sys.exc_info(), 79)
                break


class Logger(threading.Thread):
    def __init__(self, log_path="jamtools.log"):
        super(Logger, self).__init__()
        # sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        self.terminal = sys.stdout
        self.log_path = log_path
        self.logtime = time.time() - 2
        self.loglist = []
        self.start()

    def run(self) -> None:
        if os.path.exists(self.log_path):
            ls = os.path.getsize(self.log_path)
            print("log size :", ls, " saving at:", self.log_path)
            if ls > 2485760:
                with open(self.log_path, "r+", encoding="utf-8") as f:
                    f.seek(ls - 1885760)
                    log = "cut the log!" + time.strftime("%Y-%m-%d %H:%M:%S:\n", time.localtime(time.time())) + f.read()
                    f.seek(0)
                    f.truncate()
                    f.write(log)
                print("log size:", os.path.getsize(self.log_path))
        self.log = open(self.log_path, "a", encoding='utf8')
        self.log.write("\n\nOPEN@" + time.strftime("%Y-%m-%d %H:%M:%S:\n", time.localtime(time.time())))
        try:
            while True:
                if len(self.loglist):
                    self.process(self.loglist.pop(0))
                else:
                    time.sleep(0.05)
        except:
            print(sys.exc_info(), "log47")

    def write(self, message):
        self.loglist.append(message)

    def process(self, message):
        self.terminal.write(message)
        now = time.time()
        timestr = ""
        if now - self.logtime > 1:
            timestr = "\n@" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())) + "-" * 40 + "\n"

        log = timestr + message
        self.log.write(log)
        if now - self.logtime > 1:
            self.logtime = now
            self.log.flush()
        self.terminal.flush()

    def flush(self):
        pass


if __name__ == '__main__':
    wsserver = MCWebSocketserver()
    wsserver.start()
    httpserver = Httpserver()
    httpserver.start()
    print("ready")
    httpserver.join()
