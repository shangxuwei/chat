import base64
import socket
import threading
import time
import traceback
import SQLTools
import json
import logging
import hashlib
logging.basicConfig(filename='log.txt',
                    format = '%(asctime)s - %(levelname)s - %(message)s - %(funcName)s',
                    level=logging.DEBUG)



class Service:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 10088))
        self.ip_pool = {}
        self.sessions = {}
        self.SQL_obj = SQLTools.SQL_Operate()
        self.ack_life = []
        self.file_cache = dict()
        self.lock = threading.RLock()

    @staticmethod
    def thread_lock(func):
        def wrap(self,*args):
            self.lock.acquire()
            func(self,*args)
            self.lock.release()
        return wrap

    @staticmethod
    def logged_in(func):
        def check(self,*args):
            if args[0] in self.ip_pool:
                return func(self,*args)
        return check

    def listen(self):
        print('开始监听')
        while True:
            try:
                data, address = self.sock.recvfrom(8192)
                hash_pack = hashlib.md5(data).hexdigest()
                header, date, user, payload = data.decode('utf-8').split("\n\n", 3)
                if header not in ['LOGIN',"REGISTER"]:
                    self.ack(hash_pack,address)
                    if hash_pack in self.ack_life:
                        continue
                    kill = threading.Thread(target=self.kill_ack_message,args=(hash_pack,))
                    kill.start()
                method = {
                    'LOGIN': [self.login, user, address, payload], # 登录
                    'REGISTER': [self.register, user, address, payload], # 注册
                    'MESSAGE': [self.save_message, user, user, date, payload], # 消息接收
                    'GET_MESSAGE_HISTORY': [self.get_msg, user], # 获取历史消息
                    'ADD': [self.save_add_request, user, payload], # 添加好友
                    'GET_ADD_REQUEST': [self.get_add_request, user], # 获取好友请求
                    'REPLY_REQUEST': [self.handle_add_request, user, payload], # 回复好友请求
                    'SEARCH': [self.search, user, payload], # 搜索用户/群聊
                    'NEW_GROUP': [self.new_group, user, payload], # 新建群聊
                    'UPLOAD': [self.upload, user, date, payload], # 上传文件
                    'GET_FILES': [self.get_files,user,payload], # 获取文件列表
                    'DOWNLOAD': [self.download, user], # 下载文件
                    'ONLINE': [self.online, user, address], # 在线心跳信息
                    'GET_CHATS': [self.get_chats, user], # 获取历史消息
                    'LOGOUT': [self.logout, user, address] # 下线
                }
                task = threading.Thread(target=method[header][0],args=(method[header][1:]))
                task.start()
            except ConnectionResetError:
                print(self.ip_pool)
            except KeyboardInterrupt:
                break
            except:
                traceback.print_exc()

    def ack(self,hash_pack: str, address: tuple[str,int]):
        ack_mag = f'ACK\n\n\n\n\n\n{hash_pack}'.encode('utf-8')
        self.sock.sendto(ack_mag, address)

    def kill_ack_message(self,ack_pak):
        self.ack_life.append(ack_pak)
        time.sleep(2)
        self.ack_life.pop(0)

    @thread_lock
    def login(self,user: str ,address: tuple ,payload: str) -> None:
        flag = self.SQL_obj.login_check(user,payload)
        if flag == 1:
            self.ip_pool[user] = address
        self.sock.sendto(str(flag).encode("utf-8"),address)
        logging.info(f"address:{address} user:{user} res:{flag}")

    @thread_lock
    def register(self,user: str,address: tuple,payload: str) -> None:
        flag = 3
        if self.check_username(user):
            flag = self.SQL_obj.register(user,payload)
        self.sock.sendto(str(flag).encode("utf-8"), address)
        logging.info(f"address:{address} user:{user} res:{flag}")

    @logged_in
    @thread_lock
    def online(self,user: str ,address: tuple) -> None:
        if user in self.ip_pool and self.ip_pool[user] !=  address:
            self.sock.sendto('LOGOUT\n\n \n\n \n\n'.encode('utf-8'),self.ip_pool[user])
        self.ip_pool[user]=address

    @staticmethod
    def check_username(user):
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
    def logout(self,user: str ,address: tuple) -> None:
        del self.ip_pool[user]
        self.sock.sendto('LOGOUT\n\n \n\n \n\n'.encode('utf-8'), address)

    @logged_in
    @thread_lock
    def save_message(self, user: str,msg_user: str,date: float, payload: str) -> None:
        target, msg = payload.split('\n', 1)
        target = json.loads(target)
        model = target[0] # is私聊
        if target[1] == 'system':
            return None
        if model:
            self.sock.sendto(f'MESSAGE\n\n{date}\n\n{msg_user}\n\n{payload}'.encode('utf-8'), self.ip_pool[user])
            if target[1] in self.ip_pool:
                self.sock.sendto(f'MESSAGE\n\n{date}\n\n{msg_user}\n\n{payload}'.encode('utf-8'),self.ip_pool[target[1]])
        else:
            for member in self.SQL_obj.get_group_members(target[1]):
                if member in self.ip_pool:
                    self.sock.sendto(f'MESSAGE\n\n{date}\n\n{msg_user}\n\n{payload}'.encode('utf-8'), self.ip_pool[member])
        self.SQL_obj.save_msg(date,user,model,target[1],msg)

    @logged_in
    @thread_lock
    def get_msg(self, user: str) -> None:
        msgs = self.SQL_obj.get_msg(1,user)
        address = self.ip_pool[user]
        for msg in msgs:
            msg = list(msg[:3]) + [msg[3].strftime('%Y-%m-%d %H:%M:%S')] + list(msg[4:])
            self.sock.sendto(('HISTORY\n\n\n\n1\n\n'+json.dumps(msg)).encode('utf-8'),address)
        msgs = self.SQL_obj.get_msg(0,user)
        for msg in msgs:
            msg = [0,msg[3].strftime('%Y-%m-%d %H:%M:%S'),msg[2],msg[1],msg[4]]
            self.sock.sendto(('HISTORY\n\n\n\n0\n\n'+json.dumps(msg)).encode('utf-8'),address)

        self.sock.sendto('HISTORY\n\n\n\n2\n\n'.encode('utf-8'),address)

    @logged_in
    @thread_lock
    def get_chats(self, user: str) -> None:
        chat_list = self.SQL_obj.get_chat_list(user)
        payload = f'CHAT_LIST\n\n \n\n \n\n{json.dumps(chat_list)}'
        self.sock.sendto(payload.encode('utf-8'),self.ip_pool[user])

    @logged_in
    @thread_lock
    def save_add_request(self,user: str, payload: str) -> None:
        model, target = json.loads(payload)
        self.SQL_obj.save_add(user, model, target)

    @logged_in
    @thread_lock
    def get_add_request(self,user: str) -> None:
        requests = self.SQL_obj.get_add_request(user)
        payload = f'ADD_RESPONSE\n\n \n\n \n\n{json.dumps(requests)}'
        self.sock.sendto(payload.encode('utf-8'),self.ip_pool[user])

    @logged_in
    @thread_lock
    def handle_add_request(self,user,payload):
        response, res = json.loads(payload)
        model = isinstance(response,list)
        target = [1,'system']
        date = time.mktime(time.localtime())
        if model:
            source_user, group_name = response
            if res:
                msg1 = f'你已同意{source_user}加入群聊{group_name}'
                msg2 = f'你已加入群聊{group_name}'
                reply_list = ([],[group_name])
                if source_user in self.ip_pool:
                    self.sock.sendto(f'CHAT_LIST\n\n\n\n\n\n{json.dumps(reply_list)}'.encode('utf-8'),self.ip_pool[source_user])
            else:
                msg1 = f'你已拒绝{source_user}加入群聊{group_name}'
                msg2 = f'你向{group_name}群聊发送的入群请求已被管理员拒绝'
        else:
            source_user = response
            if res:
                msg1 = f'{source_user}已成为你的好友'
                msg2 = f'{user}已成为你的好友'
                reply_list = ([user],[])
                if source_user in self.ip_pool:
                    self.sock.sendto(f'CHAT_LIST\n\n\n\n\n\n{json.dumps(reply_list)}'.encode('utf-8'),self.ip_pool[source_user])
            else:
                msg1 = f'你已拒绝{source_user}的好友申请'
                msg2 = f'{user}拒绝了你的好友申请'
        if user in self.ip_pool:
            self.sock.sendto(f"MESSAGE\n\n{date}\n\nsystem\n\n{json.dumps(target)}\n{msg1}".encode('utf-8'),self.ip_pool[user])
        if source_user in self.ip_pool:
            self.sock.sendto(f"MESSAGE\n\n{date}\n\nsystem\n\n{json.dumps(target)}\n{msg2}".encode('utf-8'),self.ip_pool[source_user])
        self.SQL_obj.save_msg(date,'system',1,user,msg1)
        self.SQL_obj.save_msg(date,'system',1,source_user,msg2)
        self.SQL_obj.deal_response(model,user,response,res)

    @logged_in
    @thread_lock
    def search(self,user: str,target: str):
        """从数据库中获取与target对应的用户和群聊

        Args:
            user: 发起请求的用户
            target: 搜索目标用户名

        Returns:
            None

        """
        res = self.SQL_obj.search(target)
        self.sock.sendto(f'SEARCH_RESPONSE\n\n \n\n \n\n{json.dumps(res)}'.encode('utf-8'),self.ip_pool[user])

    @logged_in
    @thread_lock
    def new_group(self,user,groupname):
        self.SQL_obj.new_group(user,groupname)

    @logged_in
    @thread_lock
    def upload(self,user,date,payload):
        target, filename, sub, block, buf, readable_hash = json.loads(payload)
        if readable_hash not in self.file_cache:
            self.file_cache[readable_hash] = [None] * block
        self.file_cache[readable_hash][sub] = base64.b64decode(buf)
        if None not in self.file_cache[readable_hash]:
            logging.info(f'received {filename}')
            byte = bytes()
            for _ in self.file_cache[readable_hash]:
                byte += _
            self.SQL_obj.save_file(filename,user,date,byte,readable_hash,target)
            del self.file_cache[readable_hash]
            msg = f'{json.dumps(target)}\n{user}已上传文件{filename}'
            self.save_message(user,'system',date,msg)

    @logged_in
    def download(self,user):
        # TODO: 下载文件
        pass

    @logged_in
    @thread_lock
    def get_files(self,user,target):
        target = json.loads(target)
        files = self.SQL_obj.get_file_list(target)
        self.sock.sendto(f"FILES\n\n \n\n \n\n{json.dumps(files)}".encode('utf-8'),self.ip_pool[user])

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
