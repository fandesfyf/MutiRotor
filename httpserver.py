#!usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2021/7/5 22:22
# @Author  : Fandes
# @FileName: httpserver.py
# @Software: PyCharm
import http.server
import mimetypes
import os
import posixpath
import re
import socket
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from socketserver import ThreadingMixIn

Work_Path = os.path.join(os.path.split(sys.argv[0])[0], "HtmlSourse")
print(Work_Path)


def get_ips():
    if sys.platform == "linux":
        # 使用os.popen()函数执行ifconfig命令，结果为file对象，将其传入cmd_file保存
        cmd_file = os.popen('ifconfig')
        # 使用file对象的read()方法获取cmd_file的内容
        cmd_result = cmd_file.read()
        # 构造用于匹配IP的匹配模式
        pattern = re.compile(r'inet *(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})')
        # 使用re模块的findall函数匹配
        ip_list = re.findall(pattern, cmd_result)
    else:
        addrs = socket.getaddrinfo(socket.gethostname(), None)
        ip_list = [ad[4][0] for ad in addrs if len(ad[4]) == 2]
    return ip_list


IPS = get_ips()
print(IPS, "端口:10590")
for ip in IPS:
    print("http://{}:10590".format(ip))


def matchip(host: str):
    requestsip = host.split(":")[0]
    if "." in requestsip:
        return requestsip
    else:
        return "127.0.0.1"


class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(">>>>>>do get\n path:", self.path)
        path = self.translate_path(self.path)
        print("respond_get path:", self.path, path)
        if path is None or not os.path.exists(path):
            self.send_error(404, "File not found")
            return
        if os.path.isdir(path):  # 如果是文件夹路径,返回文件列表页面
            f = self.list_directory(path)
            self.send_a_file_chunk(f)
            return
        else:
            if os.path.getsize(path) > 1048576:
                self.respond_send_Slice_file(path)
                return
            else:
                self.respond_send_file(path)
                return

    def respond_send_Slice_file(self, path):
        chunksize = 204800
        print("get 大文件")
        f = None
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        fs = os.fstat(f.fileno())
        if "Range" in self.headers.keys():
            start, b = str(self.headers["Range"]).replace("bytes=", "").split("-")
            if b != "" and b != fs[6] and b != fs[6] - 1:
                end = int(b) + 1
            else:
                end = fs[6]
            print("chunk", start, b, fs[6])
        else:
            start = 0
            end = fs[6]
        start, end = int(start), int(end)

        self.send_response(206)
        self.send_header("Content-type", ctype)
        self.send_header("Content-Range", "bytes {}-{}/{}".format(start, end, fs[6]))
        self.send_header("Content-Length", str(end - start))
        self.send_header("Last-Modified", self.date_time_string(int(fs.st_mtime)))
        self.end_headers()
        print(self.headers)

        self.send_a_file_chunk(f, (start, end))

    def respond_send_file(self, path):  # 发送小文件
        print("get 小文件")
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        else:
            self.send_response(200)
            self.send_header("Content-type", ctype)
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(int(fs.st_mtime)))
            self.end_headers()
            self.send_a_file_chunk(f)

    def send_a_file_chunk(self, f, chunk: tuple = None):
        print("send chunk", chunk)
        chunksize = 1048576
        try:
            if chunk is None:
                line = f.read(chunksize)
                while line:
                    self.send_data(line)
                    line = f.read(chunksize)

            else:
                f.seek(chunk[0])
                total = chunk[1] - chunk[0]
                while total > chunksize:
                    self.send_data(f.read(chunksize))
                    total -= chunksize
                self.send_data(f.read(total))

            f.close()
        except WindowsError:
            print(sys.exc_info(), 103)

    def send_data(self, line):
        if type(line) is str:
            self.wfile.write(line.encode("utf-8"))
        else:
            self.wfile.write(line)

    def do_HEAD(self):
        print("do head")
        self.do_GET()

    def do_POST(self):  # 暂时没有用到,懒得删了
        print("do post", self.path)
        # print(self.headers)
        post_data = self.rfile.read(int(self.headers['content-length'])).decode()
        print(post_data)

    # json.dumps()# 将python对象编码成Json字符串
    # json.loads() # 将Json字符串解码成python对象
    # json.dump() # 将python中的对象转化成json储存到文件中
    # json.load()# 将文件中的json的格式转化成python对象提取出来
    def response_post(self, code: int = 200, jsonstr="{}", Content_type="text/plain", ):
        # s = json.dumps(jsonstr)
        self.send_response(code)
        self.send_header("Content-type", Content_type)
        self.send_header("Content-Length", str(len(jsonstr)))
        self.end_headers()
        self.wfile.write(jsonstr.encode())

    def translate_path(self, path):
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = [_f for _f in words if _f]
        print(words)
        if self.path == "/":
            return os.path.join(Work_Path, "html/index.html")
        else:
            if len(words):
                if words[0] in ["html", "css", "js", "img", "favicon.ico"]:
                    p = os.path.join(Work_Path,words[0] + path.split(words[0])[1])
                    return p
        return None

    def guess_type(self, path):
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init()  # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',  # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
    })


class httpserver(threading.Thread):
    def __init__(self):
        super(httpserver, self).__init__()
        self.http_handler = SimpleHTTPRequestHandler
        self.threadingServer = ThreadingServer(("", 10590), self.http_handler)

    def run(self):
        self.threadingServer.serve_forever()
        print("http server started!")


class ThreadingServer(ThreadingMixIn, http.server.HTTPServer):
    pass


if __name__ == '__main__':
    print("start")
    server = httpserver()
    server.start()
    server.join()
    print("end")
