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

        listen = Thread(target=self.listen)
        listen.start()

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
            pkt = data.decode('utf-8').split("\n\n",3)
            method[pkt[0]](pkt)

    def online(self):
        pass
    def send(self,header,date,name,payload):
        msg = f"{header}\n\n{date}\n\n{name}\n\n{payload}".encode('utf-8')
        retry = 0
        while not self.ack_check(hash(f'{header}{date}{name}')) and retry <= 5:
            self.sock.sendto(msg, self.service)
            time.sleep(1)
            retry += 1
        return retry <= 5

    def ack(self,pkt):
        header = pkt[1]
        date = pkt[2]
        name = pkt[3]
        print(f'ack:{header}{date}{name}')
        self.rcv.append(hash(f'{header}{date}{name}'))

    def ack_check(self, flag):
        if flag not in self.rcv:
            return False
        self.rcv.remove(flag)
        return True

    def message(self,pkt):
        header, date, name, payload = pkt
        t = time.localtime(float(date))
        date = f'{t.tm_year},{t.tm_mon},{t.tm_mday},{t.tm_hour}:{t.tm_min}:{t.tm_sec}'

        print(f'[{date}]{name}: {payload}')

    def login(self):
        pass

    def register(self):
        pass

    def chat(self,message):
        header = 'MESSAGE'
        t = time.localtime()
        date = time.mktime(t)
        name = self.user
        flag = self.send(header,date,name,message)
        return flag


    def upload(self):
        pass

    def download(self):
        pass

    def error(self,pkt):
        print('error')

if __name__ == '__main__':
    client = Client()
    while True:
        msg = input('>>>')
        print('\r'+' '*(len(msg)+3)+'\r')
        client.chat(msg)
