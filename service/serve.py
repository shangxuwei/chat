import base64
import hashlib
import json
import logging
import socket
import threading
import time
import traceback

from service import SQLTools

logging.basicConfig(filename='service_log.txt',
                    format = '%(asctime)s - %(levelname)s - %(message)s - %(funcName)s',
                    level=logging.DEBUG)
logging.disable(logging.DEBUG)

BUF_SIZE = 1024 # 上传下载分片字节大小

def time_FloatToStr(f_time: float):
    t = time.localtime(f_time)
    date = f'{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}'
    return date

class Service:
    """服务端运行类

    提供了用户登录，注册，聊天消息处理，文件上传下载功能

    Attributes:
        self.sock: socket对象
        self.ip_pool: 在线用户ip字典
        self.SQL_obj: 数据库操作对象
        self.ack_life: ack消息存活队列
        self.up_file_cache: 文件上传缓存
        self.dw_file_cache: 文件下载缓存
    """
    def __init__(self):
        """初始化类"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 10088))
        self.ip_pool = {}
        self.SQL_obj = SQLTools.SQL_Operate()
        self.ack_life = []
        self.up_file_cache = dict()
        self.dw_file_cache = dict()
        self.lock = threading.RLock()

    @staticmethod
    def thread_lock(func):
        """多线程，线程资源锁，装饰器"""
        def wrap(self,*args):
            self.lock.acquire()
            res = func(self,*args)
            self.lock.release()
            return res
        return wrap

    @staticmethod
    def logged_in(func):
        """操作鉴权装饰器"""
        def check(self,*args):
            # if args[0] in self.ip_pool:
            return func(self,*args)
        return check

    def listen(self):
        """消息监听器"""
        print('开始监听')
        while True:
            try:
                data, address = self.sock.recvfrom(9216)
                hash_pack = hashlib.md5(data).hexdigest()
                data = json.loads(data)
                if data['header'] not in ['LOGIN',"REGISTER"]:
                    self.ack(hash_pack,address)
                    if hash_pack in self.ack_life:
                        continue
                    kill = threading.Thread(target=self.kill_ack_message,args=(hash_pack,))
                    kill.start()
                else:
                    # login 和 register 需要指定回复ip
                    data['address'] = address
                method = {
                    'LOGIN': self.login, # 登录
                    'REGISTER': self.register, # 注册
                    'MESSAGE': self.save_message, # 消息接收
                    'GET_MESSAGE_HISTORY': self.get_msg, # 获取历史消息
                    'ADD': self.save_add_request, # 添加好友
                    'GET_ADD_REQUEST': self.get_add_request, # 获取好友请求
                    'REPLY_REQUEST': self.handle_add_request, # 回复好友请求
                    'SEARCH': self.search, # 搜索用户/群聊
                    'NEW_GROUP': self.new_group, # 新建群聊
                    'UPLOAD': self.upload, # 上传文件
                    'GET_FILES': self.get_files, # 获取文件列表
                    'DOWNLOAD': self.download, # 下载文件
                    'GET_CHATS': self.get_chats, # 获取好友列表
                    'LOGOUT': self.logout # 下线
                }
                task = threading.Thread(target=method[data['header']],args=(data,))
                task.start()
            except ConnectionResetError:
                print(self.ip_pool)
            except KeyboardInterrupt:
                break
            except:
                traceback.print_exc()

    def ack(self, ack_md5: str, address: tuple[str,int]) -> None:
        """回复ack包

        Args:
            ack_md5: 消息包md5值
            address: 目标地址

        Returns:

        """
        data = {
            'header': 'ACK',
            'md5': ack_md5
        }
        self.sock.sendto(json.dumps(data).encode('utf-8'), address)

    def kill_ack_message(self, ack_pak: str) -> None:
        """ack有效期队列维护

        Args:
            ack_pak: 消息包md5值

        Returns:
            None
        """
        self.ack_life.append(ack_pak)
        time.sleep(2)
        self.ack_life.pop(0)

    @thread_lock
    def login(self, data: dict) -> None:
        """登录请求处理

        Args:
            data:
                header: 'LOGIN',
                user: 用户名 (str),
                pwd: 密码md5值 (str),
                address: ip地址 (tuple[str,int])

        Returns:
            None
        """
        if data['user'] in self.ip_pool.keys():
            flag = 3
        else:
            flag = self.SQL_obj.login_check(data['user'],data['pwd'])
            if flag == 1:
                self.ip_pool[data['user']] = data['address']
        self.sock.sendto(str(flag).encode("utf-8"),data['address'])
        logging.info(f"address:{data['address']} user:{data['user']} res:{flag}")

    @thread_lock
    def register(self, data: dict) -> None:
        """注册请求处理

        Args:
            data:
                header: 'REGISTER',
                user: 用户名 (str),
                pwd: 密码md5值 (str),
                address: ip地址 (tuple[str,int])

        Returns:
            None
        """
        flag = 3
        if self.check_username(data['user']):
            flag = self.SQL_obj.register(data['user'],data['pwd'])
        self.sock.sendto(str(flag).encode("utf-8"), data['address'])
        logging.info(f"address:{data['address']} user:{data['user']} res:{flag}")

    @staticmethod
    def check_username(user: str) -> bool:
        """检测用户名中是否包含非法字符

        Args:
            user: 用户名

        Returns:
            一个布尔值表示是否通过
        """
        Invalid_Character = [' ','!','@',"'",'[',']','/','\\']
        Invalid_Name = ['None','system']
        for _ in Invalid_Character:
            if _ in user:
                return False
        for _ in Invalid_Name:
            if _ == user:
                return False
        return True

    @logged_in
    @thread_lock
    def logout(self, data: dict) -> None:
        """登出用户

        Args:
            data:
                user: 用户名
                address: 用户ip

        Returns:
            None
        """
        reply_data = {
            'header': 'LOGOUT'
        }
        try:
            self.sock.sendto(json.dumps(reply_data).encode('utf-8'), self.ip_pool[data['user']])
            del self.ip_pool[data['user']]
        except KeyError:
            pass

    @logged_in
    @thread_lock
    def save_message(self, data: dict) -> None:
        """保存消息

        Args:
            data:
                header: 'MESSAGE',
                date: 时间戳 (float),
                source: 用户名 (str),
                target: 收信目标 (list[int,str]),
                message: 消息内容 (str)

        Returns:
            None
        """
        model = data['target'][0] # is私聊
        if data['target'][1] == 'system':
            return None
        self.SQL_obj.save_msg(time_FloatToStr(data['date']),data['source'],model,data['target'][1],data['message'])
        self.send_message(data)

    def send_message(self, data: dict) -> None:
        """转发消息至客户端

        Args:
            data:
                header: 'MESSAGE',
                date: 时间戳 (float),
                source: 用户名 (str),
                target: 收信目标 (list[int,str]),
                message: 消息内容 (str)
        Returns:
            None
        """
        if data['target'][0]: # 私聊
            self.sock.sendto(json.dumps(data).encode('utf-8'), self.ip_pool[data['source']])
            if data['target'][1] in self.ip_pool:
                self.sock.sendto(json.dumps(data).encode('utf-8'), self.ip_pool[data['target'][1]])
        else:
            for member in self.SQL_obj.get_group_members(data['target'][1]):
                if member in self.ip_pool:
                    self.sock.sendto(json.dumps(data).encode('utf-8'), self.ip_pool[member])


    @logged_in
    @thread_lock
    def get_msg(self, data: dict) -> None:
        """获取指定目标可获得的历史消息

        Args:
            data:
                header: 'GET_MESSAGE_HISTORY',
                user: 用户名 (str)

        Returns:
            None
        """
        msgs = self.SQL_obj.get_msg(1,data['user'])
        address = self.ip_pool[data['user']]
        for msg in msgs:
            msg = list(msg[:3]) + [msg[3].strftime('%Y-%m-%d %H:%M:%S')] + list(msg[4:])
            reply_data = {
                'header': 'HISTORY',
                'model': 1,
                'msg': msg
            }
            self.sock.sendto(json.dumps(reply_data).encode('utf-8'),address)
        msgs = self.SQL_obj.get_msg(0,data['user'])
        for msg in msgs:
            msg = [0,msg[3].strftime('%Y-%m-%d %H:%M:%S'),msg[2],msg[1],msg[4]]
            reply_data = {
                'header': 'HISTORY',
                'model': 0,
                'msg': msg
            }
            self.sock.sendto(json.dumps(reply_data).encode('utf-8'),address)
        reply_data = {
            'header': 'HISTORY',
            'model': 2,
            'msg': None
        }
        self.sock.sendto(json.dumps(reply_data).encode('utf-8'),address)

    @logged_in
    @thread_lock
    def get_chats(self, data: dict) -> None:
        """获取好友/群聊列表

        Args:
            data:
                header: 'GET_CHATS',
                user: 请求用户名

        Returns:
            None
        """
        chat_list = self.SQL_obj.get_chat_list(data['user'])
        reply_data = {
            'header': 'CHAT_LIST',
            'friends': chat_list[0],
            'groups': chat_list[1]
        }
        self.sock.sendto(json.dumps(reply_data).encode('utf-8'),self.ip_pool[data['user']])

    @logged_in
    @thread_lock
    def save_add_request(self, data: dict) -> None:
        """保存好友请求

        Args:
            data:
                header: 'ADD',
                user: 发起人名称 (str),
                model: 标识添加好友/群聊，好友为 1 群聊为 0 (int),
                target: 目标名称 (str)

        Returns:
            None
        """
        self.SQL_obj.save_add(data['user'], data['model'], data['target'])

    @logged_in
    @thread_lock
    def get_add_request(self, data: dict) -> None:
        """获取指定用户好友请求

        Args:
            data:
                header: 'GET_ADD_REQUEST',
                user: 用户名 (str)

        Returns:
            None
        """
        requests = self.SQL_obj.get_add_request(data['user'])
        reply_data = {
            'header': 'ADD_RESPONSE',
            'my_friend_requests': requests[0],
            'my_group_requests': requests[1],
            'friends': requests[2],
            'groups': requests[3]
        }
        self.sock.sendto(json.dumps(reply_data).encode('utf-8'),self.ip_pool[data['user']])

    @logged_in
    @thread_lock
    def handle_add_request(self, data: dict) -> None:
        """回复好友请求

        Args:
            data:
                header: 'REPLY_REQUEST',
                user: 处理人用户名 (str),
                target: 处理目标 字符串标识用户，列表标识群聊(str | list)，
                res: 结果 1 同意， 2 拒绝 (int)

        Returns:
            None
        """
        model = isinstance(data['target'],list)
        self.SQL_obj.deal_response(model, data['user'], data['target'], data['res'])
        self.reply_handle_add(model, data)

    def reply_handle_add(self, model: bool, data: dict):
        """回复处理好友请求结果

        Args:
            model: 私聊/群聊标记
            data:
                header: 'REPLY_REQUEST',
                user: 处理人用户名 (str),
                target: 处理目标 字符串标识用户，列表标识群聊(str | list)，
                res: 结果 1 同意， 2 拒绝 (int)

        Returns:

        """
        date = time.time()
        reply_list = ([],[])
        if model:
            source_user, group_name = data['target']
            if data['res']:
                msg1 = f'你已同意{source_user}加入群聊{group_name}'
                msg2 = f'你已加入群聊{group_name}'
                reply_list = ([],[group_name])
            else:
                msg1 = f'你已拒绝{source_user}加入群聊{group_name}'
                msg2 = f'你向{group_name}群聊发送的入群请求已被管理员拒绝'
        else:
            source_user = data['target']
            if data['res']:
                msg1 = f'{source_user}已成为你的好友'
                msg2 = f"{data['user']}已成为你的好友"
                reply_list = ([data['user']],[])
            else:
                msg1 = f'你已拒绝{source_user}的好友申请'
                msg2 = f"{data['user']}拒绝了你的好友申请"
        if data['res']:
            if source_user in self.ip_pool:
                add_replay = {
                    'header': 'CHAT_LIST',
                    'friends': reply_list[0],
                    'groups': reply_list[1]
                }
                self.sock.sendto(json.dumps(add_replay).encode('utf-8'),self.ip_pool[source_user])
        reply_msg_data = {
            'header': 'MESSAGE',
            'date': date,
            'source': 'system',
            'target': [1,'system'],
        }
        if data['user'] in self.ip_pool:
            reply_msg_data['message'] = msg1
            self.sock.sendto(json.dumps(reply_msg_data).encode('utf-8'),self.ip_pool[data['user']])
        if source_user in self.ip_pool:
            reply_msg_data['message'] = msg2
            self.sock.sendto(json.dumps(reply_msg_data).encode('utf-8'),self.ip_pool[source_user])
        self.SQL_obj.save_msg(time_FloatToStr(time.time()),'system',1,data['user'],msg1)
        self.SQL_obj.save_msg(time_FloatToStr(time.time()),'system',1,source_user,msg2)


    @logged_in
    @thread_lock
    def search(self, data: dict) -> None:
        """从数据库中获取与target对应的用户和群聊

        Args:
            data:
                header: 'SEARCH',
                user: 请求用户名 (str),
                target: 搜索目标 (str)

        Returns:
            None
        """
        res = self.SQL_obj.search(data['target'])
        reply_data = {
            'header': 'SEARCH_RESPONSE',
            'name': data['target'],
            'user': res[0],
            'group': res[1]
        }
        self.sock.sendto(json.dumps(reply_data).encode('utf-8'),self.ip_pool[data['user']])

    @logged_in
    @thread_lock
    def new_group(self, data: dict) -> None:
        """新建群聊

        Args:
            data:
                header: 'NEW_GROUP',
                user: 用户名/管理员名称 (str),
                groupname: 群聊名称 (str)

        Returns:
            None
        """
        self.SQL_obj.new_group(data['user'],data['groupname'])

    @logged_in
    @thread_lock
    def upload(self, data: dict) -> None:
        """处理上传文件

        Args:
            data:
                header: 'UPLOAD',
                user: 用户名 (str),
                target: 收件目标 (list[int,str]),
                filename: 文件名 (str),
                sub: 文件块号 (int),
                block: 文件块数 (int),
                buf: 文件数据<base64编码> (str),
                md5: 文件md5值

        Returns:
            None
        """
        if data['md5'] not in self.up_file_cache:
            self.up_file_cache[data['md5']] = [None] * data['block']
        self.up_file_cache[data['md5']][data['sub']] = base64.b64decode(data['buf'])
        if None not in self.up_file_cache[data['md5']]:
            logging.info(f"{data['user']} upload:{data['filename']} md5:{data['md5']}")
            byte = bytes()
            for _ in self.up_file_cache[data['md5']]:
                byte += _
            self.SQL_obj.save_file(data['filename'],data['user'],time_FloatToStr(time.time()),byte,data['md5'],data['target'])
            del self.up_file_cache[data['md5']]

            msg_data = {
                'header': 'MESSAGE',
                'date': time.time(),
                'source': data['user'],
                'target': data['target'],
                'message': f"{data['user']}已上传文件{data['filename']}"
            }
            self.send_message(msg_data)


    @logged_in
    @thread_lock
    def download(self, data: dict) -> None:
        """处理下载请求

        Args:
            data:
                header: 'DOWNLOAD',
                user: 发起请求的用户 (str),
                sub: 块号 (int | None),
                block: 块数 (int | None),
                file_name: 文件名称 (str),
                md5: 文件md5值 (str)

        Returns:
            None
        """
        if data['sub'] is None:
            data['sub'] = 0
        if data['sub'] == data['block']:
            try:
                del self.dw_file_cache[data['md5']]
            except KeyError:
                pass
            return
        if data['md5'] not in self.dw_file_cache.keys():
            logging.info(f"{data['user']} require file:{data['filename']}  / md5:{data['md5']}")
            buf = self.SQL_obj.get_file(data['filename'], data['md5'])
            self.dw_file_cache[data['md5']] = base64.b64encode(buf)
        if data['block'] is None:
            data['block'] = len(self.dw_file_cache[data['md5']]) // BUF_SIZE + 1
        buf = self.dw_file_cache[data['md5']][data['sub'] * BUF_SIZE: (data['sub']+1) * BUF_SIZE].decode()
        reply_data = {
            'header': 'DOWNLOAD',
            'sub': data['sub'],
            'block': data['block'],
            'filename': data['filename'],
            'md5': data['md5'],
            'buf': buf
        }
        self.sock.sendto(json.dumps(reply_data).encode('utf-8'),self.ip_pool[data['user']])


    @logged_in
    @thread_lock
    def get_files(self, data: dict) -> None:
        """获取目标聊天中的文件列表

        Args:
            data:
                header: 'GET_FILES',
                user: 用户名 (str),
                target: 目标聊天 (list[int,str])

        Returns:
            None
        """
        files = self.SQL_obj.get_file_list(data['target'])
        reply_data = {
            'header': 'FILES',
            'files': files
        }
        self.sock.sendto(json.dumps(reply_data).encode('utf-8'),self.ip_pool[data['user']])

if __name__ == "__main__":
    service = Service()
    listen = threading.Thread(target=service.listen)
    listen.daemon=True
    listen.start()
    while True:
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            print('service stopped')
            break
