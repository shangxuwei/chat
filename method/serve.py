import socket
import time

class Service:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 10088))
        self.ip_cache = []

    def listen(self):
        while True:
            data, address = self.sock.recvfrom(4096)
            if data:
                pass
            if address not in self.ip_cache:
                self.ip_cache.append(address)
            try:
                header, date, name, payload = data.decode('utf-8').split("\n\n",3)
                self.sock.sendto(f'ACK\n\n{header}\n\n{date}\n\n{name}'.encode('utf-8'),address)
                method = {
                    'LOGIN': self.login,
                    'REGISTER': self.register,
                    'MESSAGE': self.message,
                    'UPLOAD': self.upload,
                    'DOWNLOAD':self.download,
                    'ONLINE':self.online
                }
                method[header](date,name,payload)
                print(f'ACK to {address},{header}, {header}{date}{name}')
            except Exception as e:
                print(e)
                print(data.decode('utf-8'))
                print('ERROR')
                self.sock.sendto('ERROR\n\n \n\n \n\n '.encode('utf-8'),address)

    def online(self):
        pass
    def login(self):
        pass

    def register(self):
        pass

    def message(self, date, name, payload):
        t = time.localtime(float(date))
        dt = f'{t.tm_year},{t.tm_mon},{t.tm_mday},{t.tm_hour}:{t.tm_min}:{t.tm_sec}'
        print(f'[{dt}]{name}:{payload}')
        for address in self.ip_cache:
            self.sock.sendto(f'MESSAGE\n\n{date}\n\n{name}\n\n{payload}'.encode('UTF-8'), address)

        # TODO: SQL操作
        pass

    def upload(self):
        pass

    def download(self):
        pass

if __name__ == "__main__":
    service = Service()
    service.listen()
