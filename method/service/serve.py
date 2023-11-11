import socket
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
        self.SQL_obj = SQLTools.SQL_Operate()

    def listen(self):
        while True:
            try:
                data, address = self.sock.recvfrom(4096)
                header, date, user, payload = data.decode('utf-8').split("\n\n", 3)
                if header not in ['LOGIN',"REGISTER"]:
                    ack_mag = f'ACK\n\n{header}\n\n{date}\n\n{user}'.encode('utf-8')
                    self.sock.sendto(ack_mag, address)
                    ack_pak = f'{header}{date}{user}'
                    logging.debug(f'ACK to {address}, {header}{date}{user}, hash:{hash(ack_pak)}')
                method = {
                    'LOGIN': [self.login, address, user, payload],
                    'REGISTER': [self.register, address, user, payload],
                    'MESSAGE': [self.message, date, user, payload],
                    'GET_FILE': [self.get_msg,user,payload],
                    'UPLOAD': self.upload,
                    'DOWNLOAD': self.download,
                    'ONLINE': [self.online, address, user],
                    'GET_CHATS':[self.get_chats,address,user]
                }
                method[header][0](*(method[header][1:]))
            except ConnectionResetError:
                print(self.ip_pool)
            except:
                traceback.print_exc()
                self.sock.sendto('ERROR\n\n \n\n \n\n '.encode('utf-8'),address)

    def online(self,address:tuple ,name:str) -> None:
        if name in self.ip_pool and self.ip_pool[name] !=  address:
            self.sock.sendto('LOGOUT\n\n \n\n \n\n'.encode('utf-8'),self.ip_pool[name])
        self.ip_pool[name]=address

    def login(self,address,user,payload):
        flag = self.SQL_obj.login_check(user,payload)
        self.sock.sendto(str(flag).encode("utf-8"),address)
        logging.info(f"address:{address} user:{user} res:{flag}")
        

    def register(self,address,user,payload):
        flag = self.SQL_obj.register(user,payload)
        self.sock.sendto(str(flag).encode("utf-8"), address)
        logging.info(f"address:{address} user:{user} res:{flag}")

    def message(self, date: str, user, payload):
        target, msg = payload.split('\n', 1)
        target = json.loads(target)
        model = int(target[0]) # is私聊

        if model:
            self.sock.sendto(f'MESSAGE\n\n{date}\n\n{user}\n\n{msg}'.encode('utf-8'), self.ip_pool[user])
            if target[1] in self.ip_pool:
                self.sock.sendto(f'MESSAGE\n\n{date}\n\n{user}\n\n{msg}'.encode('utf-8'),self.ip_pool[target[1]])
        else:
            for member in self.SQL_obj.get_group_members(target[1]):
                if member in self.ip_pool:
                    self.sock.sendto(f'MESSAGE\n\n{date}\n\n{user}\n\n{msg}'.encode('utf-8'), self.ip_pool[member])
        self.SQL_obj.save_msg(date,user,model,target[1],msg)

    def get_msg(self,user,payload):
        target = json.loads(payload)
        model = int(target[0])
        msgs = self.SQL_obj.get_msg(model,user,target[1])
        print(msgs)

    def get_chats(self,address,user):
        chat_list = self.SQL_obj.get_chat_list(user)
        payload = f'CHAT_LIST\n\n \n\n \n\n{json.dumps(chat_list)}'
        self.sock.sendto(payload.encode('utf-8'),address)

    def upload(self):
        pass

    def download(self):
        pass

if __name__ == "__main__":
    service = Service()
    print(service.SQL_obj.get_group_members('public'))
    service.listen()
