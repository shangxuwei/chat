import socket
import time
from threading import Thread
import tkinter as tk
from tkinter import ttk
import json
import hashlib
from local import SqliteTools
from concurrent.futures import ThreadPoolExecutor
import tkinter.messagebox
import base64
import os
from typing import *

class Client:
    def __init__(self,user=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 0))
        # 服务端地址
        self.service = ('127.0.0.1', 10088)
        self.user = user

        self.ackpool = []
        self.message_pool = ThreadPoolExecutor(max_workers=200)
        self.online = 0

        self.messagebox: tk.Text = None # 聊天消息框

        self.chat_list: ttk.Treeview = None # 好友/群组 列表
        self.chat_fir_list = '' # 好友列表
        self.chat_group_list = '' # 群组列表

        self.search_text:tk.Text = None # 搜索框
        self.res_friend: tk.Label = None # 用户搜索结果
        self.res_group: tk.Label = None # 群组搜索结果
        self.add_fri_Btn: tk.Button = None # 添加好友按钮
        self.add_group_Btn: tk.Button = None # 添加群聊按钮
        self.request_list: ttk.Treeview = None # 请求列表
        self.my_fri_requests = '' # 我发送的请求
        self.my_group_requests = ''
        self.fri_requests = '' # 好友请求
        self.group_requests = '' # 加入群聊请求

        self.file_table: ttk.Treeview = None

        self.chat_page = []

        self.file_cache = {}

        self.Sql_obj:SqliteTools.SqlTools = None

    @staticmethod
    def sql_operate(func):
        def init(self,*args):
            self.Sql_obj = SqliteTools.SqlTools(self.user, model='run')
            try:
                func(self,*args)
            finally:
                if self.Sql_obj is not None:
                    self.Sql_obj.cur.close()
                    self.Sql_obj.conn.close()
                    self.Sql_obj = None
        return init

    def login(self,user: str,password: str) -> int:
        header = 'LOGIN'
        date = time.mktime(time.localtime())
        md5_object = hashlib.md5()
        md5_object.update(password.encode('utf-8'))
        md5_result = md5_object.hexdigest()
        msg = f"{header}\n\n{date}\n\n{user}\n\n{md5_result}".encode('utf-8')
        self.sock.sendto(msg,self.service)
        try:
            self.sock.settimeout(1)
            data, address = self.sock.recvfrom(8192)
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
                self.Sql_obj = SqliteTools.SqlTools(self.user, model='init')
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
        while self.online:
            data, address = self.sock.recvfrom(4096)
            header,date,user,payload = data.decode('utf-8').split('\n\n',3)
            method = {
                'MESSAGE': [self.message,date,user,payload],
                'DOWNLOAD': self.download,
                'LOGOUT':[self.logout],
                'ACK': [self.ack,payload],
                'FILES': [self.file_list,payload],
                'CHAT_LIST': [self.save_chat_list,payload],
                'ADD_RESPONSE': [self.update_requests_list,payload],
                'SEARCH_RESPONSE': [self.search_response,payload],
                'HISTORY':[self.history,user,payload]
            }
            method[header][0](*(method[header][1:]))

    def get_history(self):
        self.sock.sendto(f'GET_MESSAGE_HISTORY\n\n\n\n{self.user}\n\n'.encode('utf-8'),self.service)

    def message_color_init(self):
        self.messagebox.tag_add('other', tk.INSERT)
        self.messagebox.tag_config('other', foreground='blue')
        self.messagebox.tag_add('me', tk.INSERT)
        self.messagebox.tag_config('me', foreground='green')
        self.messagebox.tag_add('system', tk.INSERT)
        self.messagebox.tag_config('system', foreground='gray')

    def insert_message(self,date: str,user: str,msg: str) -> None:
        self.messagebox.configure(state='normal')
        if user == self.user:
            self.messagebox.insert(tk.INSERT, f'[{date}]{user}: {msg}\n','me')
        elif user == 'system':
            self.messagebox.insert(tk.INSERT, f'[{date}]{user}: {msg}\n','system')
        else:
            self.messagebox.insert(tk.INSERT, f'[{date}]{user}: {msg}\n','other')
        self.messagebox.insert(tk.INSERT,'-' * 110 +'\n','system')
        self.messagebox.see('end')
        self.messagebox.configure(state='disabled')

    @sql_operate
    def message(self,date,source_user,payload):
        target, msg = payload.split('\n', 1)
        target = json.loads(target)
        t = time.localtime(float(date))
        date = f'{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}'
        if source_user != self.user and target[0] == 1:
            self.Sql_obj.save_msg(target[0], date, source_user, source_user, msg)
        else:
            self.Sql_obj.save_msg(target[0], date, target[1], source_user, msg)
        if target == self.chat_page or (self.user == target[1] and self.chat_page[1] == source_user):
            self.insert_message(date,source_user,msg)

    @sql_operate
    def history(self,model,payload):
        if model == '0':
            msg = json.loads(payload)
            self.Sql_obj.save_msg(*msg)
        elif model == '1':
            msg = json.loads(payload)
            page = msg[1] if msg[1] != self.user else msg[2]
            self.Sql_obj.save_msg(int(model), msg[3], page, msg[2], msg[4])
        elif model == '2':
            self.switch_chat(1,'system')
            tkinter.messagebox.showinfo(title='esaychat:system',message='历史记录同步完成')

    def logout(self):
        self.online=0

    def keep(self):
        while self.online:
            self.send("ONLINE",'online')
            time.sleep(60)

    def send(self,header: str,payload: str,model:Literal['message','file'] = 'message') -> None:
        def send_message(head: str, message: str, model) -> None:
            date = time.mktime(time.localtime())
            msg = f"{head}\n\n{date}\n\n{self.user}\n\n{message}".encode('utf-8')
            retry = 0
            ack_hash = hashlib.md5(msg).hexdigest()
            self.ackpool.append(ack_hash)
            if model == 'message':
                while self.ack_check(ack_hash) and retry <= 5:
                    self.sock.sendto(msg, self.service)
                    time.sleep(2)
                    retry += 1
                if retry > 5:
                    tkinter.messagebox.showerror(title=head,message='connect timeout')
            elif model == 'file':
                while self.ack_check(ack_hash):
                    self.sock.sendto(msg, self.service)
                    time.sleep(2)
        if model == 'message':
            work = Thread(target=send_message,args=(header,payload,model))
            work.start()
        elif model == 'file':
            self.message_pool.submit(send_message,header,payload,model)

    def ack(self, payload) -> None:
        try:
            self.ackpool.remove(payload)
        except:
            pass

    def ack_check(self, flag: str) -> bool:
        if flag in self.ackpool:
            return True
        return False

    def chat(self,message: str):
        header = 'MESSAGE'
        message = json.dumps(self.chat_page) + '\n' + message
        self.send(header,message)

    def get_chat_list(self):
        header = 'GET_CHATS'
        self.send(header,' ')

    @sql_operate
    def save_chat_list(self,payload):
        friends = json.loads(payload)[0]
        groups = json.loads(payload)[1]
        self.Sql_obj.save_chats(1,friends)
        self.Sql_obj.save_chats(0,groups)
        for _ in friends:
                self.chat_list.insert(self.chat_fir_list, index='end', tags=[json.dumps([1,_])], text=_)
        for _ in groups:
                self.chat_list.insert(self.chat_group_list, index='end', tags=[json.dumps([0,_])], text=_)

    def get_requests_list(self):
        self.send('GET_ADD_REQUEST','')

    @staticmethod
    def format_request(text: str | list[str, str]) -> str:
        if isinstance(text, list):
            return f'{text[0]} -> {text[1]}'
        return text

    @sql_operate
    def update_requests_list(self,payload: str):
        requests = json.loads(payload)
        trees = [self.my_fri_requests, self.my_group_requests, self.fri_requests, self.group_requests]
        self.Sql_obj.save_add_requests(1,requests[0])
        self.Sql_obj.save_add_requests(0,requests[1])
        for reqs,tree in zip(requests,trees):
            for _ in reqs:
                node = self.request_list.insert(tree,'end',_,text=self.format_request(_))
                if tree in trees[-2:]:
                    self.request_list.insert(node, 'end', tags=[json.dumps([_,1])], text='同意')
                    self.request_list.insert(node, 'end', tags=[json.dumps([_,0])], text='拒绝')

    def handle_add_request(self, target: str | list, res: int) -> None:
        """回复好友请求

        Args:
            target: 一个字符串或者列表，字符串表示用户名，列表则为[用户名，群聊]
            res: 一个整数，1为同意，0为拒绝

        Returns:
            None
        """
        if res == 1:
            if isinstance(target,str):
                self.save_chat_list(json.dumps(([target],[])))
        self.send('REPLY_REQUEST',json.dumps([target,res]))

    def search(self,target: str) -> None:
        """发起搜索请求

        Args:
            target: 搜索目标用户名

        Returns:
            None
        """
        self.send('SEARCH',target)

    @sql_operate
    def search_response(self,payload: str) -> None:
        """响应搜索请求，在addfriend_page页面label处显示结果

        Args:
            payload: 一个字符串，表示搜索结果，类型为json.dumps([user,group])

        Returns:
            None
        """
        name, user_exist, group_exist = json.loads(payload)
        self.res_friend.configure(text=name,fg=('green' if user_exist else 'red'))
        self.res_group.configure(text=name,fg=('green' if group_exist else 'red'))
        if not user_exist:
            self.add_fri_Btn.configure(text='用户不存在')
        elif name == self.user or self.Sql_obj.friend_is_exist(user_exist):
            self.add_fri_Btn.configure(text='好友已存在')
        elif self.Sql_obj.fir_request_is_exist(name):
            self.add_fri_Btn.configure(text='已发送请求')
        else:
            self.add_fri_Btn.configure(state='normal',text='添加好友')
        if not group_exist:
            self.add_group_Btn.configure(state='normal',text='创建群聊')
        elif self.Sql_obj.group_is_exist(name):
            self.add_group_Btn.configure(text='已在群聊中')
        elif self.Sql_obj.group_request_is_exist(name):
            self.add_group_Btn.configure(text='请求已发送')
        else:
            self.add_group_Btn.configure(state='normal',text='添加群聊')

    @sql_operate
    def add_request(self,model:int ,target: str) -> None:
        """发起添加好友/群聊请求

        Args:
            model: 一个整数表示添加好友或群聊，1添加好友，0添加群聊
            target: 一个字符串表示目标名称

        Returns:
            None
        """
        header = 'ADD'
        payload = json.dumps([model,target])
        self.send(header,payload)
        self.Sql_obj.save_add_request(model,target)
        self.request_list.insert(self.my_fri_requests if model else self.my_group_requests,'end',text=target)

    @sql_operate
    def new_group(self, groupname: str) -> None:
        """发起新建群聊请求

        Args:
            groupname: 群聊名称

        Returns:
            None
        """
        self.send('NEW_GROUP',groupname)
        self.Sql_obj.save_chat(0,groupname)
        self.request_list.insert(self.my_fri_requests,'end',text=groupname)
        self.save_chat_list(json.dumps([[],[groupname]]))
        tkinter.messagebox.showinfo('新建群聊','新建群聊成功')

    def upload(self,files: list[bytes]) -> None:
        for _ in files:
            with open(_.decode('gbk'),'rb') as file:
                buf = file.read()
                b64_buf = base64.b64encode(buf)
                file_name, extension = os.path.splitext(os.path.basename(files[0].decode('gbk')))
                filename = file_name+extension
                readable_hash = hashlib.md5(buf).hexdigest()
                size = 4096
                block = len(base64.b64encode(buf)) // size + 1
                sub = 0
                while sub <= block - 1:
                    payload = json.dumps([self.chat_page,filename, sub, block, b64_buf[sub*size:(sub+1)*size].decode(),readable_hash])
                    self.send('UPLOAD',payload,'file')
                    sub += 1

    def get_file_list(self):
        self.send('GET_FILES',json.dumps(self.chat_page),'message')

    def file_list(self,payload):
        files = json.loads(payload)
        for file in files:
            self.file_table.insert('','end',values=file)

    def download(self):
        # TODO:下载文件
        pass

    @sql_operate
    def switch_chat(self, model: int, target: str) -> None:
        self.chat_page=[model, target]
        msgs = self.Sql_obj.get_msg(model,target)
        for msg in msgs:
            self.insert_message(msg[2],msg[4],msg[5])
