import socket
import threading
import trace
import time
import traceback
import SQLTools
import json
import logging
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
                data, address = self.sock.recvfrom(4096)
                print(address)
                header, date, user, payload = data.decode('utf-8').split("\n\n", 3)
                if header not in ['LOGIN',"REGISTER"]:
                    ack_pak = f'{header}{date}{user}'
                    self.ack(header,date,user,address)
                    if ack_pak in self.ack_life:
                        continue
                    kill = threading.Thread(target=self.kill_ack_message,args=(ack_pak,))
                    kill.start()
                method = {
                    'LOGIN': [self.login, user, address, payload],
                    'REGISTER': [self.register, user, address, payload],
                    'MESSAGE': [self.message, user, date, payload],
                    'GET_MESSAGE_HISTORY': [self.get_msg,user,address],
                    'UPLOAD': [self.upload, user],
                    'DOWNLOAD': [self.download, user],
                    'ONLINE': [self.online, user, address],
                    'GET_CHATS':[self.get_chats,user,address],
                    'LOGOUT':[self.logout, user, address]
                }
                method[header][0](*(method[header][1:]))
            except ConnectionResetError:
                print(self.ip_pool)
            except KeyboardInterrupt:
                break
            except:
                traceback.print_exc()
                self.sock.sendto('ERROR\n\n \n\n \n\n '.encode('utf-8'),address)

    def ack(self,header: str,date: str,user: str,address: tuple[str,int]):
        ack_mag = f'ACK\n\n{header}\n\n{date}\n\n{user}'.encode('utf-8')
        self.sock.sendto(ack_mag, address)
        ack_pak = f'{header}{date}{user}'
        logging.debug(f'ACK to {address}, {ack_pak}, hash:{hash(ack_pak)}')

    def kill_ack_message(self,ack_pak):
        self.ack_life.append(ack_pak)
        time.sleep(2)
        self.ack_life.pop(0)


    def online(self,user: str ,address: tuple) -> None:
        if user in self.ip_pool and self.ip_pool[user] !=  address:
            self.sock.sendto('LOGOUT\n\n \n\n \n\n'.encode('utf-8'),self.ip_pool[user])
        self.ip_pool[user]=address

    def login(self,user: str ,address: tuple ,payload: str) -> None:
        flag = self.SQL_obj.login_check(user,payload)
        if flag == 1:
            self.ip_pool[user] = address
        self.sock.sendto(str(flag).encode("utf-8"),address)
        logging.info(f"address:{address} user:{user} res:{flag}")

    def register(self,user: str,address: tuple,payload: str) -> None:
        flag = self.SQL_obj.register(user,payload)
        self.sock.sendto(str(flag).encode("utf-8"), address)
        logging.info(f"address:{address} user:{user} res:{flag}")

    @logged_in
    def logout(self,user: str ,address: tuple) -> None:
        del self.ip_pool[user]
        self.sock.sendto('LOGOUT\n\n \n\n \n\n'.encode('utf-8'), address)

    @logged_in
    def message(self, user: str, date: float, payload: str) -> None:
        target, msg = payload.split('\n', 1)
        target = json.loads(target)
        model = target[0] # is私聊

        if model:
            self.sock.sendto(f'MESSAGE\n\n{date}\n\n{user}\n\n{payload}'.encode('utf-8'), self.ip_pool[user])
            if target[1] in self.ip_pool:
                self.sock.sendto(f'MESSAGE\n\n{date}\n\n{user}\n\n{payload}'.encode('utf-8'),self.ip_pool[target[1]])
        else:
            for member in self.SQL_obj.get_group_members(target[1]):
                if member in self.ip_pool:
                    self.sock.sendto(f'MESSAGE\n\n{date}\n\n{user}\n\n{payload}'.encode('utf-8'), self.ip_pool[member])
        self.SQL_obj.save_msg(date,user,model,target[1],msg)

    @logged_in
    def get_msg(self,user: str,address: tuple) -> None:
        msgs = self.SQL_obj.get_msg(1,user)
        for msg in msgs:
            msg = list(msg[:3]) + [msg[3].strftime('%Y-%m-%d %H:%M:%S')] + list(msg[4:])
            self.sock.sendto(('HISTORY\n\n\n\n1\n\n'+json.dumps(msg)).encode('utf-8'),address)
        msgs = self.SQL_obj.get_msg(0,user)
        for msg in msgs:
            msg = [0,msg[3].strftime('%Y-%m-%d %H:%M:%S'),msg[2],msg[1],msg[4]]
            self.sock.sendto(('HISTORY\n\n\n\n0\n\n'+json.dumps(msg)).encode('utf-8'),address)

        self.sock.sendto('HISTORY\n\n\n\n2\n\n'.encode('utf-8'),address)

    @logged_in
    def get_chats(self,user: str,address: tuple) -> None:
        chat_list = self.SQL_obj.get_chat_list(user)
        payload = f'CHAT_LIST\n\n \n\n \n\n{json.dumps(chat_list)}'
        self.sock.sendto(payload.encode('utf-8'),address)

    @logged_in
    def upload(self,user):
        pass

    @logged_in
    def download(self,user):
        pass

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