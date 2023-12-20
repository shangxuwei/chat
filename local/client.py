import base64
import hashlib
import json
import logging
import os
import socket
import time
import tkinter as tk
import tkinter.messagebox
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from tkinter import ttk
from typing import *

from local import SqliteTools

logging.basicConfig(filename='local_log.txt',
                    format = '%(asctime)s - %(levelname)s - %(message)s - %(funcName)s',
                    level=logging.DEBUG)
logging.disable(logging.DEBUG)

BUF_SIZE = 1024 # 上传下载分片字节大小

class Client:
    """客户端运行类

    提供了登录，注册，收发信，文件上传下载功能函数

    Attributes:
        self.sock: socket对象
        self.service: 服务端ip及端口号
        self.user: 登录用户名
        self.ackpool: ack消息队列
        self.message_pool: 文件上传消息线程池
        self.online: 在线标识
        self.chat_page: 聊天页面
        self.file_cache: 下载文件缓存
        self.SQL_obj: 数据库操作对象
    """
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 0))
        # 服务端地址
        self.service = ('127.0.0.1', 10088)
        self.user = None

        self.ackpool = []
        self.message_pool = ThreadPoolExecutor(max_workers=40)
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

        self.up_down_task: tk.StringVar = None # 上传下载消息

        self.file_table: ttk.Treeview = None # 文件列表

        self.chat_page = []

        self.file_cache = {}

        self.Sql_obj: SqliteTools.SqlTools = None

    @staticmethod
    def sql_operate(func):
        """数据库操作装饰器"""
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

    @staticmethod
    def thread_pool_callback(worker):
        """线程池故障捕获"""
        logging.debug("called thread pool executor callback function")
        worker_exception = worker.exception()
        if worker_exception:
            logging.exception("Worker return exception: {}".format(worker_exception))

    def get_work_queue(self):
        """下载进度刷新"""
        while True:
            try:
                if self.up_down_task is None:
                    time.sleep(0.5)
                    continue
                if self.message_pool._work_queue.qsize() > 0:
                    flag = '正在传输'
                else:
                    flag = '无连接'
                download_task = len(self.file_cache.keys())
                percent = None
                if download_task != 0:
                    data = list(self.file_cache.values())[0]
                    percent = '%.2f' % ((len(data)-data.count(None))/len(data)*100)
                msg = f'文件传输: {flag} | 下载任务数: {download_task} : {percent}% (百分比仅显示第一个任务)'
                self.up_down_task.set(msg)
                time.sleep(2)
            except RuntimeError:
                break

    def login(self, user: str, password: str) -> int:
        """发起登录请求

        Args:
            user: 用户名
            password: 用户密码

        Returns:
            None
        """
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
                keep = Thread(target=self.keep)
                task = Thread(target=self.get_work_queue)
                listen.daemon = True
                keep.daemon = True
                task.daemon = True
                listen.start()
                keep.start()
                task.start()
                self.Sql_obj = SqliteTools.SqlTools(self.user, model='init')
            return int(data)
        except:
            return 2

    def register(self, user: str, password: str) -> int:
        """发起注册请求

        Args:
            user: 注册用户名
            password: 注册用户密码

        Returns:
            None
        """
        header = 'REGISTER'
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
            return int(data)
        except:
            return 2

    def listen(self):
        """消息监听器"""
        while self.online:
            data, address = self.sock.recvfrom(9216)
            header,date,user,payload = data.decode('utf-8').split('\n\n',3)
            method = {
                'MESSAGE': [self.message,date,user,payload],
                'DOWNLOAD': [self.download,payload],
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
        """发起历史消息获取请求"""
        self.sock.sendto(f'GET_MESSAGE_HISTORY\n\n\n\n{self.user}\n\n'.encode('utf-8'),self.service)

    def message_color_init(self):
        """消息颜色初始化"""
        self.messagebox.tag_add('other', tk.INSERT)
        self.messagebox.tag_config('other', foreground='blue')
        self.messagebox.tag_add('me', tk.INSERT)
        self.messagebox.tag_config('me', foreground='green')
        self.messagebox.tag_add('system', tk.INSERT)
        self.messagebox.tag_config('system', foreground='gray')

    def insert_message(self,date: str,user: str,msg: str) -> None:
        """向文本框中插入消息

        Args:
            date: 时间
            user: 发信用户
            msg: 消息内容

        Returns:
            None
        """
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
    def message(self, date: str, source_user: str, payload: str) -> None:
        """处理接受到消息

        Args:
            date: 发信时间
            source_user: 发信人
            payload: 消息数据包，[收信目标,消息内容]

        Returns:
            None
        """
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
        else:
            page = target[1] if target[1] != self.user and target != 0 else source_user
            self.chat_list.tag_configure(json.dumps([target[0], page]), foreground='blue')

    @sql_operate
    def history(self, model: str, payload: str) -> None:
        """处理历史消息

        Args:
            model: 一个字符串标志操作目标，0标识群聊，1标识私聊，2标识消息接受完成
            payload: 消息数据包

        Returns:
            None
        """
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
        """退出登录"""
        self.online=0

    def keep(self):
        """在线心跳"""
        while self.online:
            self.send("ONLINE",'online')
            time.sleep(60)

    def send(self, header: str, payload: str, model:Literal['message','file'] = 'message') -> None:
        """消息发送函数

        Args:
            header: 请求头
            payload: 请求载荷
            model: 请求模式,文件传输/消息传输

        Returns:
            None
        """
        def send_message(head: str, message: str, mod: str) -> None:
            date = time.mktime(time.localtime())
            msg = f"{head}\n\n{date}\n\n{self.user}\n\n{message}".encode('utf-8')
            retry = 0
            ack_hash = hashlib.md5(msg).hexdigest()
            self.ackpool.append(ack_hash)
            if mod == 'message':
                while self.ack_check(ack_hash) and retry <= 5:
                    self.sock.sendto(msg, self.service)
                    time.sleep(2)
                    retry += 1
                if retry > 5:
                    tkinter.messagebox.showerror(title=head,message='connect timeout')
            elif mod == 'file':
                while self.ack_check(ack_hash):
                    self.sock.sendto(msg, self.service)
                    time.sleep(2)
        if model == 'message':
            work = Thread(target=send_message,args=(header,payload,model))
            work.start()
        elif model == 'file':
            task = self.message_pool.submit(send_message,header,payload,model)
            task.add_done_callback(self.thread_pool_callback)


    def ack(self, payload: str) -> None:
        """ack消息处理

        Args:
            payload: ack包md5值

        Returns:
            None
        """
        try:
            self.ackpool.remove(payload)
        except:
            pass

    def ack_check(self, flag: str) -> bool:
        """检测ack包是否存在"""
        if flag in self.ackpool:
            return True
        return False

    def chat(self, message: str):
        """发送聊天消息

        Args:
            message: 消息数据包,[收信目标]\n消息

        Returns:
            None
        """
        header = 'MESSAGE'
        message = json.dumps(self.chat_page) + '\n' + message
        self.send(header,message)

    def get_chat_list(self):
        """发起获得聊天列表请求"""
        header = 'GET_CHATS'
        self.send(header,' ')

    @sql_operate
    def save_chat_list(self,payload: str):
        """保存聊天列表

        Args:
            payload: 聊天列表数据包

        Returns:
            None
        """
        friends = json.loads(payload)[0]
        groups = json.loads(payload)[1]
        self.Sql_obj.save_chats(1,friends)
        self.Sql_obj.save_chats(0,groups)
        for _ in friends:
                self.chat_list.insert(self.chat_fir_list, index='end', tags=[json.dumps([1,_])], text=_)
        for _ in groups:
                self.chat_list.insert(self.chat_group_list, index='end', tags=[json.dumps([0,_])], text=_)

    def get_requests_list(self):
        """发起获取好友请求列表请求"""
        self.send('GET_ADD_REQUEST','')

    @sql_operate
    def update_requests_list(self,payload: str) -> None:
        """更新好友请求列表

        Args:
            payload: 好友请求数据包

        Returns:
            None
        """
        def format_request(text: str | list[str, str]) -> str:
            if isinstance(text, list):
                return f'{text[0]} -> {text[1]}'
            return text
        requests = json.loads(payload)
        trees = [self.my_fri_requests, self.my_group_requests, self.fri_requests, self.group_requests]
        self.Sql_obj.save_add_requests(1,requests[0])
        self.Sql_obj.save_add_requests(0,requests[1])
        for reqs,tree in zip(requests,trees):
            for _ in reqs:
                node = self.request_list.insert(tree,'end',_,text=format_request(_))
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

    def search(self, target: str) -> None:
        """发起搜索请求

        Args:
            target: 搜索目标用户名

        Returns:
            None
        """
        self.send('SEARCH',target)

    @sql_operate
    def search_response(self, payload: str) -> None:
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
    def add_request(self, model:int ,target: str) -> None:
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

    def upload(self, files: list[bytes]) -> None:
        """上传文件

        Args:
            files: 上传文件的的目录位置，二进制格式

        Returns:
            None
        """
        for _ in files:
            with open(_.decode('gbk'),'rb') as file:
                buf = file.read()
                b64_buf = base64.b64encode(buf)
                file_name, extension = os.path.splitext(os.path.basename(files[0].decode('gbk')))
                filename = file_name+extension
                readable_hash = hashlib.md5(buf).hexdigest()
                block = len(base64.b64encode(buf)) // BUF_SIZE + 1
                sub = 0
                while sub <= block - 1:
                    payload = json.dumps([self.chat_page,
                                          filename,
                                          sub,
                                          block,
                                          b64_buf[sub*BUF_SIZE:(sub+1)*BUF_SIZE].decode(),
                                          readable_hash])
                    self.send('UPLOAD',payload,'file')
                    sub += 1

    def get_file_list(self):
        """获取文件列表"""
        self.send('GET_FILES',json.dumps(self.chat_page),'message')

    def file_list(self, payload: str):
        """处理文件列表

        Args:
            payload: 文件列表数据包

        Returns:
            None
        """
        files = json.loads(payload)
        for file in files:
            self.file_table.insert('','end',values=file)

    def get_download(self, sub: None | int,block: None | int, filename: str, md5: str) -> None:
        """发起下载请求

        Args:
            sub: 块号
            block: 块数
            filename: 文件名
            md5: 文件md5值

        Returns:
            None
        """
        payload = json.dumps([sub,block,filename,md5])
        self.send('DOWNLOAD',payload,'file')

    def download(self, payload: str) -> None:
        """处理文件下载数据包

        Args:
            payload: 文件下载数据包

        Returns:
            None
        """
        sub, block, filename, md5, byte = json.loads(payload)
        if md5 not in self.file_cache.keys():
            self.file_cache[md5] = [None] * block
        if sub > 0 and self.file_cache[md5][sub - 1] is None:
            self.get_download(sub-1,block,filename,md5)
            return
        self.file_cache[md5][sub] = base64.b64decode(byte)
        if None not in self.file_cache[md5]:
            buf = bytes()
            for _ in self.file_cache[md5]:
                buf += _
            with open(filename,'wb') as file:
                file.write(buf)
            self.get_download(block,block,filename,md5)
            del self.file_cache[md5]
            tkinter.messagebox.showinfo('下载',f'{filename}下载完成')
            return
        self.get_download(sub+1,block,filename,md5)

    @sql_operate
    def switch_chat(self, model: int, target: str) -> None:
        """切换页面

        Args:
            model: 页面标识，标志私聊或群聊
            target: 聊天对象

        Returns:
            None
        """
        self.chat_page=[model, target]
        msgs = self.Sql_obj.get_msg(model,target)
        self.chat_list.tag_configure(json.dumps(self.chat_page), foreground='black')
        for msg in msgs:
            self.insert_message(msg[2],msg[4],msg[5])
