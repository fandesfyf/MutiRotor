"""
======================
@author:Fandes
@time:2022/4/24:20:37
======================
"""

class WebSocketserver(QThread):
    def __init__(self, host="", port=8787):
        super(WebSocketserver, self).__init__()
        self.host, self.port = host, port
        self.on_running = True

    async def requestcallback(self, websocket, path):  # websockets.legacy.server.WebSocketServerProtocol
        print("socket request path:", path, websocket.remote_address)
        if path == "/upload":
            print("upload connected")
            try:
                task = asyncio.get_event_loop().create_task(self.onrec(websocket))
                # task2 = asyncio.get_event_loop().create_task(self.heartbeat(websocket))
                await task
                # await task2
            except:
                print(sys.exc_info(), 31)
                return

        else:
            print("unknown request")
            await websocket.send("unknown request")
        print("end")

    def run(self):
        print("websocket start")
        self.new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.new_loop)
        self.websockets_server = websockets.serve(self.requestcallback, self.host, self.port, ping_interval=0.5)
        self.new_loop.run_until_complete(self.websockets_server)
        self.new_loop.run_forever()

    # def sendmessage(self,message):
    #     self.websockets_server.

    async def onrec(self, websocket):
        while True:
            recv_text = await websocket.recv()
            print("ws rec", recv_text)
            print(json.loads(recv_text))
            await websocket.send("1")

    async def heartbeat(self, websocket):
        while True:
            # print("heartbeat")
            await websocket.send("0")
            await asyncio.sleep(0.5)