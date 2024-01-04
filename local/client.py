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

def time_FloatToStr(f_time: float):
    t = time.localtime(f_time)
    date = f'{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}'
    return date

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
        self.upload_pool = ThreadPoolExecutor(max_workers=40)
        self.download_pool = ThreadPoolExecutor(max_workers=40)
        self.online = 0
        self.cookie = None

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
                if self.upload_pool._work_queue.qsize() > 0:
                    flag = '正在传输'
                else:
                    flag = '无连接'
                download_task = len(self.file_cache.keys())
                percent = None
                if download_task != 0:
                    data = list(self.file_cache.values())[0]
                    percent = '%.2f' % ((len(data)-data.count(None))/len(data)*100)
                msg = f'文件上传: {flag} | 下载任务数: {download_task} : {percent}% (百分比仅显示第一个任务)'
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
        md5_object = hashlib.md5()
        md5_object.update(password.encode('utf-8'))
        md5_result = md5_object.hexdigest()
        data = {
            'header': 'LOGIN',
            'user': user,
            'pwd': md5_result
        }
        msg = json.dumps(data).encode('utf-8')
        self.sock.sendto(msg,self.service)
        # Wait for a reply
        try:
            self.sock.settimeout(1)
            data, address = self.sock.recvfrom(8192)
            self.sock.settimeout(None)
            data = json.loads(data)
            if data['res'] == 1:
                self.online = 1
                self.user = user
                self.cookie = data['cookie']
                listen = Thread(target=self.listen)
                task = Thread(target=self.get_work_queue)
                listen.daemon = True
                task.daemon = True
                listen.start()
                task.start()
                self.Sql_obj = SqliteTools.SqlTools(self.user, model='init')
            return data['res']
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
        md5_object = hashlib.md5()
        md5_object.update(password.encode('utf-8'))
        md5_result = md5_object.hexdigest()
        data = {
            'header': 'REGISTER',
            'user': user,
            'pwd': md5_result
        }
        msg = json.dumps(data).encode('utf-8')
        self.sock.sendto(msg,self.service)
        # Wait for a reply
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
            data = json.loads(data)
            method = {
                'MESSAGE': self.message,
                'DOWNLOAD': self.download,
                'LOGOUT':self.logout,
                'ACK': self.ack,
                'FILES': self.handle_file_list,
                'CHAT_LIST': self.save_chat_list,
                'ADD_RESPONSE': self.update_requests_list,
                'SEARCH_RESPONSE': self.search_response,
                'HISTORY': self.history
            }
            method[data['header']](data)

    def get_history(self):
        """发起历史消息获取请求"""
        data = {
            'header': 'GET_MESSAGE_HISTORY',
            'user': self.user
        }
        self.send(data)

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
    def message(self, data: dict) -> None:
        """处理接受到消息

        Args:
            data:
                header: 'MESSAGE',
                date: 时间戳 (float),
                source: 发信用户名 (str),
                target: 收信目标 (list[int,str]),
                message: 消息内容 (str)

        Returns:
            None
        """
        if data['source'] != self.user and data['target'][0] == 1:
            self.Sql_obj.save_msg(data['target'][0],
                                  time_FloatToStr(data['date']),
                                  data['source'],
                                  data['source'],
                                  data['message'])
        else:
            self.Sql_obj.save_msg(data['target'][0],
                                  time_FloatToStr(data['date']),
                                  data['target'][1],
                                  data['source'],
                                  data['message'])
        if data['target'] == self.chat_page or (self.user == data['target'][1] and self.chat_page[1] == data['source']):
            self.insert_message(time_FloatToStr(data['date']), data['source'], data['message'])
        else:
            page = data['target'][1] if data['target'][1] != self.user else data['source']
            self.chat_list.tag_configure(json.dumps([data['target'][0], page]), foreground='blue')

    @sql_operate
    def history(self, data: dict) -> None:
        """处理历史消息

        Args:
            data:
                header: 'HISTORY'
                model: 一个字符串标志操作目标，0标识群聊，1标识私聊，2标识消息接受完成
                payload: 消息数据包

        Returns:
            None
        """
        if data['model'] == 0:
            self.Sql_obj.save_msg(*data['msg'])
        elif data['model'] == 1:
            msg = data['msg']
            page = msg[1] if msg[1] != self.user else msg[2]
            self.Sql_obj.save_msg(data['model'], msg[3], page, msg[2], msg[4])
        elif data['model'] == '2':
            self.switch_chat(1,'system')

    def get_logout(self):
        data = {
            'header': 'LOGOUT',
            'user': self.user
        }
        self.send(data)

    def logout(self, data):
        """退出登录"""
        self.online=0

    def send(self, data: dict, model:Literal['message','upload','download'] = 'message') -> None:
        """消息发送函数

        Args:
            data: json数据包的
            model: 请求模式,文件传输/消息传输

        Returns:
            None
        """
        def send_message() -> None:
            data['cookie'] = [self.user, self.cookie]
            msg = json.dumps(data).encode('utf-8')
            retry = 0
            ack_hash = hashlib.md5(msg).hexdigest()
            self.ackpool.append(ack_hash)
            if model == 'message':
                while self.ack_check(ack_hash) and retry <= 5:
                    self.sock.sendto(msg, self.service)
                    time.sleep(2)
                    retry += 1
                if retry > 5:
                    tkinter.messagebox.showerror(title=data['header'], message='connect timeout')
            elif model in ['upload','download']:
                while self.ack_check(ack_hash):
                    self.sock.sendto(msg, self.service)
                    time.sleep(2)
        if model == 'message':
            work = Thread(target=send_message)
            work.start()
        elif model == 'upload':
            task = self.upload_pool.submit(send_message)
            task.add_done_callback(self.thread_pool_callback)
        elif model == 'download':
            task = self.download_pool.submit(send_message)
            task.add_done_callback(self.thread_pool_callback)


    def ack(self, data: dict) -> None:
        """ack消息处理

        Args:
            data:
                header: 'ACK',
                md5: 数据包md5值 (str)

        Returns:
            None
        """
        try:
            self.ackpool.remove(data['md5'])
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
            message: 发送的消息

        Returns:
            None
        """
        data = {
            'header': 'MESSAGE',
            'date' : time.mktime(time.localtime()),
            'source': self.user,
            'target': self.chat_page,
            'message': message
        }
        self.send(data, model='message')

    def get_chat_list(self):
        """发起获得聊天列表请求"""
        data = {
            'header': 'GET_CHATS',
            'user': self.user
        }
        self.send(data)

    @sql_operate
    def save_chat_list(self, data: dict):
        """保存聊天列表

        Args:
            data:
                header: 'CHAT_LIST',
                friends: 好友列表 (list),
                groups: 群聊列表 (list),

        Returns:
            None
        """
        self.Sql_obj.save_chats(1,data.get('friends',[]))
        self.Sql_obj.save_chats(0,data.get('groups',[]))
        for _ in data.get('friends',[]):
                self.chat_list.insert(self.chat_fir_list, index='end', tags=[json.dumps([1,_])], text=_)
        for _ in data.get('groups',[]):
                self.chat_list.insert(self.chat_group_list, index='end', tags=[json.dumps([0,_])], text=_)

    def get_requests_list(self):
        """发起获取好友请求列表请求"""
        data = {
            'header': 'GET_ADD_REQUEST',
            'user': self.user
        }
        self.send(data)

    @sql_operate
    def update_requests_list(self, data: dict) -> None:
        """更新好友请求列表

        Args:
            data:
                header: 'ADD_RESPONSE',
                my_friend_requests: 本地用户发起的好友请求 (list),
                my_group_requests: 本地用户发起的入群请求 (list),
                friends: 本地用户收到的好友请求 (list),
                groups: 本地用户收到的入群请求 (list)

        Returns:
            None
        """
        def format_request(text: str | list[str, str]) -> str:
            if isinstance(text, list):
                return f'{text[0]} -> {text[1]}'
            return text
        requests = list(data.values())[1:]
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
                self.save_chat_list({
                    'friends': [target]
                })
        data = {
            'header': 'REPLY_REQUEST',
            'user': self.user,
            'target': target,
            'res': res
        }
        self.send(data)

    def search(self, target: str) -> None:
        """发起搜索请求

        Args:
            target: 搜索目标用户名

        Returns:
            None
        """
        data = {
            'header': 'SEARCH',
            'user': self.user,
            'target': target
        }
        self.send(data)

    @sql_operate
    def search_response(self, data: dict) -> None:
        """响应搜索请求，在addfriend_page页面label处显示结果

        Args:
            data:
                header: 'SEARCH_RESPONSE',
                name: 搜索目标名称 (str),
                user: 用户是否存在 (bool),
                group: 群聊是否存在 (bool)

        Returns:
            None
        """
        name, user_exist, group_exist = list(data.values())[1:]
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
        data = {
            'header': header,
            'user': self.user,
            'model': model,
            'target': target
        }
        self.send(data)
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
        data = {
            'header': 'NEW_GROUP',
            'user': self.user,
            'groupname': groupname
        }
        self.send(data)
        self.Sql_obj.save_chat(0,groupname)
        self.request_list.insert(self.my_fri_requests,'end',text=groupname)
        self.save_chat_list({
            'groups': [groupname]
        })
        tkinter.messagebox.showinfo('新建群聊','新建群聊成功')

    def upload(self, files: list[bytes]) -> None:
        """上传文件

        Args:
            files: 上传文件的的目录位置，二进制格式

        Returns:
            None
        """
        for _ in files:
            with open(_,'rb') as file:
                buf = file.read()
                b64_buf = base64.b64encode(buf)
                file_name, extension = os.path.splitext(os.path.basename(_))
                filename = file_name+extension
                md5 = hashlib.md5(buf).hexdigest()
                block = len(base64.b64encode(buf)) // BUF_SIZE + 1
                sub = 0
                while sub <= block - 1:
                    data = {
                        'header': 'UPLOAD',
                        'user': self.user,
                        'target': self.chat_page,
                        'filename': filename,
                        'sub': sub,
                        'block': block,
                        'buf': b64_buf[sub*BUF_SIZE:(sub+1)*BUF_SIZE].decode(),
                        'md5': md5
                    }
                    self.send(data, 'upload')
                    sub += 1

    def get_file_list(self):
        """获取文件列表"""
        data = {
            'header': 'GET_FILES',
            'user': self.user,
            'target': self.chat_page
        }
        self.send(data)

    def handle_file_list(self, data: dict):
        """处理文件列表

        Args:
            data:
                header: 'FILES]
                files: 文件列表数据包 (list)

        Returns:
            None
        """
        for file in data['files']:
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
        data = {
            'header': 'DOWNLOAD',
            'user': self.user,
            'sub': sub,
            'block': block,
            'filename': filename,
            'md5': md5
        }
        self.send(data, 'download')

    def download(self, data: dict) -> None:
        """处理文件下载数据包

        Args:
            data:
                header: 'DOWNLOAD'
                sub: 块号 (int)
                block: 块数 (int)
                filename: 文件名 (str)
                md5: 文件md5 (str)
                buf: 文件数据<base64编码> (str)

        Returns:
            None
        """
        if data['md5'] not in self.file_cache.keys():
            self.file_cache[data['md5']] = [None] * data['block']
        if data['sub'] > 0 and self.file_cache[data['md5']][data['sub'] - 1] is None:
            self.get_download(data['sub']-1, data['block'], data['filename'] ,data['md5'])
            return
        self.file_cache[data['md5']][data['sub']] = base64.b64decode(data['buf'])
        if None not in self.file_cache[data['md5']]:
            buf = bytes()
            for _ in self.file_cache[data['md5']]:
                buf += _
            with open(data['filename'], 'wb') as file:
                file.write(buf)
            del self.file_cache[data['md5']]
            tkinter.messagebox.showinfo('下载',f"{data['filename']}下载完成")
        self.get_download(data['sub']+1,data['block'],data['filename'],data['md5'])

    def close_threads_pool(self):
        self.download_pool.shutdown(wait=False,cancel_futures=True)
        self.upload_pool.shutdown(wait=False,cancel_futures=True)

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
