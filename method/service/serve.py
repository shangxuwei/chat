import socket
import trace
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
            data, address = self.sock.recvfrom(4096)
            try:
                header, date, user, payload = data.decode('utf-8').split("\n\n", 3)
                method = {
                    'LOGIN': [self.login, address, user, payload],
                    'REGISTER': [self.register, address, user, payload],
                }
                method[header][0](*(method[header][1:]))
            except:
                traceback.print_exc()

    def login(self,address,user,payload):
        flag = self.SQL_obj.login_check(user,payload)
        self.sock.sendto(str(flag).encode("utf-8"),address)
        logging.info(f"address:{address} user:{user} res:{flag}")
        

    def register(self,address,user,payload):
        flag = self.SQL_obj.register(user,payload)
        self.sock.sendto(str(flag).encode("utf-8"), address)
        logging.info(f"address:{address} user:{user} res:{flag}")

if __name__ == "__main__":
    service = Service()
    service.listen()
