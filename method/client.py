import socket
import time
from threading import Thread

class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 0))
        # 服务端地址
        self.service = ('127.0.0.1', 10088)
        self.user = '123'

        self.rcv = []

    def listen(self):
        while True:
            data, address = self.sock.recvfrom(4096)
            method = {
                'MESSAGE': self.message,
                'LOGIN': self.login,
                'REGISTER': self.register,
                'UPLOAD': self.upload,
                'DOWNLOAD': self.download,
                'ERROR': self.error,
                'ACK': self.ack
            }
            header, date, name, payload = data.decode('utf-8').split("\n\n",1)
            method[header](date,name,payload)

    def ack(self,date,name,payload):
        self.rcv.append(hash(date+name+payload))

    def ack_check(self, flag):
        while flag not in self.rcv:
            return False

        return True
    def message(self,date,name,payload):
        print(f'[{date}]{name}: {payload}')

    def login(self):
        pass

    def register(self):
        pass

    def chat(self,message):
        header = 'MESSAGE'
        t = time.localtime()
        date = f'{t.tm_year},{t.tm_mon},{t.tm_mday},{t.tm_hour}:{t.tm_min}:{t.tm_sec}'
        name = self.user
        msg = f"{header}\n\n{date}\n\n{name}\n\n{message}".encode('utf-8')
        retry = 0
        while not self.ack_check(hash(date+self.user+message)) and retry <= 5:
            self.sock.sendto(msg, self.service)
            time.sleep(1)


    def upload(self):
        pass

    def download(self):
        pass

    def error(self,message):
        print('error')

if __name__ == '__main__':
    client = Client()
    listen = Thread(target=client.listen)
    listen.start()
    client.chat('hello')
    print(1)
