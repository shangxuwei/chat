import socket
import time
from threading import Thread

class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 本地端地址
        self.sock.bind(('0.0.0.0',10087))
        # 服务端地址
        self.service = ('127.0.0.1', 10088)

    def listen(self):
        while True:
            data, address = self.sock.recvfrom(4096)
            method = {
                'MESSAGE': self.message,
                'LOGIN': self.login,
                'REGISTER': self.register,
                'CHAT': self.chat,
                'UPLOAD': self.upload,
                'DOWNLOAD': self.download,
                'ERROR': self.error
            }
            header, message = data.decode('utf-8').split("\n\n",3)
            method[header](message)



    def message(self):
        pass

    def login(self):
        pass

    def register(self):
        pass

    def chat(self):
        t = time.localtime()
        date = f'{t.tm_year},{t.tm_mon},{t.tm_mday},{t.tm_hour}:{t.tm_min}:{t.tm_sec}'
        name = 'shangxuwei'
        msg = f"{date}\n\n{name}\n\n你好".encode('utf-8')
        sent = self.sock.sendto(msg, self.service)
        print(sent)
        data, server = self.sock.recvfrom(4096)
        print(data.decode("utf-8"))

    def upload(self):
        pass

    def download(self):
        pass

    def error(self):
        pass

if __name__ == '__main__':
    client = Client()
    listen = Thread(target=client.listen)
    listen.start()
    client.chat()
