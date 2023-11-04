import socket
import time
from threading import Thread
import hashlib


class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 0))
        # 服务端地址
        self.service = ('127.0.0.1', 10088)
        self.user = 'none'

        self.ackpool = []
        self.online = 0


    def listen(self):
        while True:
            data, address = self.sock.recvfrom(4096)
            header,date,user,payload = data.decode('utf-8').split('\n\n',3)
            method = {
                'MESSAGE': [self.message,date,user,payload],
                'UPLOAD': self.upload,
                'DOWNLOAD': self.download,
                'ERROR': self.error,
                'ACK': [self.ack,date,user,payload]
            }
            method[header][0](*(method[header][1:]))

    def keep(self):
        while True:
            date = time.mktime(time.localtime())
            self.send("ONLINE",date,self.user,'online')
            time.sleep(60)

    def send(self,header,date,user,payload):
        msg = f"{header}\n\n{date}\n\n{user}\n\n{payload}".encode('utf-8')
        retry = 0
        while not self.ack_check(hash(f'{header}{date}{user}')) and retry <= 5:
            self.sock.sendto(msg, self.service)
            time.sleep(1)
            retry += 1
        return retry <= 5

    def ack(self, header, date, user):
        self.ackpool.append(hash(f'{header}{date}{user}'))

    def ack_check(self, flag):
        if flag not in self.ackpool:
            return False
        self.ackpool.remove(flag)
        return True

    def message(self,date,user,payload):
        t = time.localtime(float(date))
        date = f'{t.tm_year},{t.tm_mon},{t.tm_mday},{t.tm_hour}:{t.tm_min}:{t.tm_sec}'

        print(f'[{date}]{user}: {payload}')
        return f'[{date}]{user}: {payload}'

    def login(self,user,password):
        header = 'LOGIN'
        date = time.mktime(time.localtime())
        md5_object = hashlib.md5()
        md5_object.update(password.encode('utf-8'))
        md5_result = md5_object.hexdigest()
        msg = f"{header}\n\n{date}\n\n{user}\n\n{md5_result}".encode('utf-8')
        self.sock.sendto(msg,self.service)
        try:
            self.sock.settimeout(1)
            data, address = self.sock.recvfrom(4096)
            self.sock.settimeout(None)
            data = data.decode("utf-8")
            if int(data):
                listen = Thread(target=self.listen)
                listen.start()
                keep = Thread(target=self.keep)
                keep.start()
            return int(data)
        except:
            return 2

    def register(self,user,password):
        header = 'REGISTER'
        date = time.mktime(time.localtime())
        md5_object = hashlib.md5()
        md5_object.update(password.encode('utf-8'))
        md5_result = md5_object.hexdigest()
        msg = f"{header}\n\n{date}\n\n{user}\n\n{md5_result}".encode('utf-8')
        self.sock.sendto(msg,self.service)
        try:
            self.sock.settimeout(1)
            data, address = self.sock.recvfrom(4096)
            self.sock.settimeout(None)
            data = data.decode("utf-8")
            return int(data)
        except:
            return 2

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

    def error(self):
        print('error')
