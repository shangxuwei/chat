import socket
import time
from threading import Thread
import tkinter as tk
import json
from typing import *
import hashlib
from method.local import SqliteTools


class Client:
    def __init__(self,user=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 0))
        # 服务端地址
        self.service = ('127.0.0.1', 10088)
        self.user = user

        self.ackpool = []

        self.online = 0

        self.messagebox = None
        self.chat_list = None
        self.fir_list = ''
        self.group_list = ''

        self.chat_page = [0,'public']

        self.Sql_obj = None


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
                listen.daemon = True
                listen.start()
                keep = Thread(target=self.keep)
                keep.daemon = True
                keep.start()
                self.Sql_read = SqliteTools.SqlTools(self.user,model='r')
            return int(data)
        except:
            return 2

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

    def listen(self):
        self.Sql_obj = SqliteTools.SqlTools(self.user)
        while self.online:
            data, address = self.sock.recvfrom(4096)
            header,date,user,payload = data.decode('utf-8').split('\n\n',3)
            method = {
                'MESSAGE': [self.message,date,user,payload],
                'UPLOAD': self.upload,
                'DOWNLOAD': self.download,
                'ERROR': [self.error,None],
                'LOGOUT':[self.logout],
                'ACK': [self.ack,date,user,payload],
                'CHAT_LIST':[self.update_chat_list,payload],
                'HISTORY':[self.history,user,payload]
            }
            method[header][0](*(method[header][1:]))
        self.Sql_obj.cur.close()
        self.Sql_obj.conn.close()
        self.Sql_obj = None

    def switch_chat(self,model,target):
        msgs = self.Sql_read.get_msg(model,target)
        for msg in msgs:
            self.insert_message(msg[2],msg[4],msg[5])


    def get_history(self):
        self.sock.sendto(f'GET_MESSAGE_HISTORY\n\n\n\n{self.user}\n\n'.encode('utf-8'),self.service)

    def insert_message(self,date,user,msg):

        self.messagebox.tag_add('other', tk.INSERT)  # 申明一个tag,在a位置使用
        self.messagebox.tag_config('other', foreground='blue')
        self.messagebox.tag_add('me', tk.INSERT)  # 申明一个tag,在a位置使用
        self.messagebox.tag_config('me', foreground='green')
        self.messagebox.configure(state='normal')
        if user == self.user:
            self.messagebox.insert(tk.INSERT, f'[{date}]{user}: {msg}\n','me')
        else:
            self.messagebox.insert(tk.INSERT, f'[{date}]{user}: {msg}\n','other')
        self.messagebox.configure(state='disabled')

    def message(self,date,user,payload):
        target, msg = payload.split('\n', 1)
        target = json.loads(target)
        if user != self.user and target[0] == 1:
            self.Sql_obj.insert_msg(target[0], date, user, user, msg)
        else:
            self.Sql_obj.insert_msg(target[0], date, target[1], user, msg)
        if target == self.chat_page or (self.user == target[1] and self.chat_page[1] == user):
            t = time.localtime(float(date))
            date = f'{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}'
            self.insert_message(date,user,msg)

    def history(self,model,payload):
        if model == '0':
            msg = json.loads(payload)
            print(msg)
            self.Sql_obj.insert_msg(*msg)
        elif model == '1':
            msg = json.loads(payload)
            page = msg[1] if msg[1] != self.user else msg[2]
            self.Sql_obj.insert_msg(int(model),msg[3],page,msg[2],msg[4])
        elif model == '2':
            print('finish')

    def logout(self):
        self.online=0

    def keep(self):
        while self.online:
            self.send("ONLINE",'online')
            time.sleep(60)

    def send(self,header,payload):
        date = time.mktime(time.localtime())
        msg = f"{header}\n\n{date}\n\n{self.user}\n\n{payload}".encode('utf-8')
        retry = 0
        self.ackpool.append(hash(f'{header}{date}{self.user}'))
        while self.ack_check(hash(f'{header}{date}{self.user}')) and retry <= 5:
            self.sock.sendto(msg, self.service)
            time.sleep(0.05)
            retry += 1
        return retry <= 5

    def ack(self, header, date, user):
        try:
            self.ackpool.remove(hash(f'{header}{date}{user}'))
        except:
            pass

    def ack_check(self, flag):
        if flag in self.ackpool:
            return True
        return False

    def chat(self,message):
        header = 'MESSAGE'
        message = json.dumps(self.chat_page) + '\n' + message
        flag = self.send(header,message)
        return flag

    def get_msg(self,chat_page):
        header = 'GET'
        self.send(header,chat_page)

    def get_chat_list(self):
        header = 'GET_CHATS'
        self.send(header,' ')

    def update_chat_list(self,payload):
        friends = json.loads(payload)[0]
        groups = json.loads(payload)[1]
        for _ in friends:
            self.chat_list.insert(self.fir_list, index='end', iid=[1,_], text=_)
        for _ in groups:
            self.chat_list.insert(self.group_list, index='end', iid=[0,_], text=_)

    def upload(self):
        pass

    def download(self):
        pass

    def error(self):
        print('error')

    @staticmethod
    def swatch_page(new_page=None,close_page: tk.Tk=None):
        if close_page is not None:
            close_page.destroy()
        if new_page is not None:
            init_window = tk.Tk()
            init_window.resizable(width=False,height=False)
            new_page(init_window)
            init_window.mainloop()

