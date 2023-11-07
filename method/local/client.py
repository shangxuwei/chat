import socket
import time
from threading import Thread
import tkinter as tk
from page import login_page,chat_page,addfriend_page
from typing import *
import hashlib

class Client:
    def __init__(self,user=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 0))
        # 服务端地址
        self.service = ('127.0.0.1', 10088)
        self.user = user

        self.ackpool = []

        self.online = 0

    @staticmethod
    def swatch_page(new_page=None,close_page: tk.Tk=None):
        if close_page is not None:
            close_page.destroy()
        if new_page is not None:
            init_window = tk.Tk()
            init_window.resizable(width=False,height=False)
            new_page(init_window)
            init_window.mainloop()

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
                self.online = 1
                self.user = user
                listen = Thread(target=self.listen)
                listen.start()
                keep = Thread(target=self.keep)
                keep.start()
            return int(data)
        except:
            return 2

    def listen(self):
        while True:
            data, address = self.sock.recvfrom(4096)
            header,date,user,payload = data.decode('utf-8').split('\n\n',3)
            method = {
                'MESSAGE': [self.message,date,user,payload],
                'UPLOAD': self.upload,
                'DOWNLOAD': self.download,
                'ERROR': [self.error,None],
                'LOGOUT':[self.logout],
                'ACK': [self.ack,date,user,payload]
            }
            method[header][0](*(method[header][1:]))

    def message(self,date,user,payload):
        t = time.localtime(float(date))
        date = f'{t.tm_year},{t.tm_mon},{t.tm_mday},{t.tm_hour}:{t.tm_min}:{t.tm_sec}'

        print(f'[{date}]{user}: {payload}')
        return f'[{date}]{user}: {payload}'
    def logout(self):
        self.online = 0

    def keep(self):
        while True:
            self.send("ONLINE",self.user,'online')
            time.sleep(60)

    def send(self,header,user,payload):
        date = time.mktime(time.localtime())
        msg = f"{header}\n\n{date}\n\n{user}\n\n{payload}".encode('utf-8')
        retry = 0
        while not self.ack_check(hash(f'{header}{date}{user}')) and retry <= 5:
            self.sock.sendto(msg, self.service)
            time.sleep(0.01)
            retry += 1
        return retry <= 5

    def ack(self, header, date, user):
        self.ackpool.append(hash(f'{header}{date}{user}'))

    def ack_check(self, flag):
        if flag not in self.ackpool:
            return False
        self.ackpool.remove(flag)
        return True

    def register(self,user: str,password: str) -> int:
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
        name = self.user
        flag = self.send(header,name,message)
        return flag

    def get_msg(self,chat_page):
        header = 'GET'
        self.send(header,self.user,chat_page)

    def upload(self):
        page

    def download(self):
        pass

    def error(self,l):
        print('error')

