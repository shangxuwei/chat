import socket
import time
import SQLTools
import logging
logging.basicConfig(filename='log.txt',
                     format = '%(asctime)s - %(levelname)s - %(message)s - %(funcName)s',
                     level=logging.DEBUG)


class Service:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 10088))
        self.ip_pool = []
        self.SQL_obj = SQLTools.SQL_Operate()

    def listen(self):
        while True:
            data, address = self.sock.recvfrom(4096)
            try:
                header, date, user, payload = data.decode('utf-8').split("\n\n", 3)
                method = {
                    'LOGIN': [self.login, address, user, payload],
                    'REGISTER': [self.register, address, user, payload],
                    'MESSAGE': [self.message, date, user, payload],
                    'UPLOAD': self.upload,
                    'DOWNLOAD': self.download,
                    'ONLINE': [self.online, address, user]
                }
                method[header][0](*(method[header][1:]))
                if header not in ['LOGIN',"REGISTER"]:
                    ack_mag = f'ACK\n\n{header}\n\n{date}\n\n{user}'.encode('utf-8')
                    self.sock.sendto(ack_mag, address)
                    ack_pak = f'{header}{date}{user}'
                    print(f'ACK to {address}, {header}, {user}, hash:{hash(ack_pak)}')
            except Exception as e:
                self.sock.sendto('ERROR\n\n \n\n \n\n '.encode('utf-8'),address)

    def online(self,address,name):
        if (name,address) not in self.ip_pool:
            self.ip_pool.append((name,address))

    def login(self,address,user,payload):
        flag = self.SQL_obj.login_check(user,payload)
        self.sock.sendto(str(flag).encode("utf-8"),address)
        logging.info(f"address:{address} user:{user} res:{flag}")
        

    def register(self,address,user,payload):
        flag = self.SQL_obj.register(user,payload)
        self.sock.sendto(str(flag).encode("utf-8"), address)
        logging.info(f"address:{address} user:{user} res:{flag}")

    def message(self, date, name, payload):
        t = time.localtime(float(date))
        dt = f'{t.tm_year},{t.tm_mon},{t.tm_mday},{t.tm_hour}:{t.tm_min}:{t.tm_sec}'
        for _,address in self.ip_pool:
            msg = f'MESSAGE\n\n{date}\n\n{name}\n\n{payload}'.encode('UTF-8')
            self.sock.sendto(msg, address)

    def upload(self):
        pass

    def download(self):
        pass

if __name__ == "__main__":
    service = Service()
    service.listen()
