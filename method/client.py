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

        listen = Thread(target=self.listen)
        listen.start()
        keep = Thread(target=self.online)
        keep.start()

    def listen(self):
        while True:
            data, address = self.sock.recvfrom(4096)
            header,date,user,payload = data.decode('utf-8').split('\n\n',3)
            method = {
                'MESSAGE': [self.message,date,user,payload],
                'LOGIN_BACK': self.login_back,
                'REGISTER_BACK': self.register_back,
                'UPLOAD': self.upload,
                'DOWNLOAD': self.download,
                'ERROR': self.error,
                'ACK': [self.ack,date,user,payload]
            }
            method[header][0](*(method[header][1:]))

    def online(self):
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
        self.send(header,date,user,md5_result)
        return 1

    def login_back(self):
        pass

    def register(self,user,password):
        header = 'REGISTER'
        date = time.mktime(time.localtime())
        md5_object = hashlib.md5()
        md5_object.update(password.encode('utf-8'))
        md5_result = md5_object.hexdigest()
        self.send(header, date, user, md5_result)
        return 2

    def register_back(self):
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

# if __name__ == '__main__':
#     client = Client()
#     while True:
#         msg = input('>>>')
#         print('\r'+' '*(len(msg)+3)+'\r')
#         client.chat(msg)
