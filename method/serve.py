import socket

class Service:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 10088))
        self.ip_cache = []

    def listen(self):
        while True:
            print('1')
            data, address = self.sock.recvfrom(4096)
            if data:
                pass
            if address not in self.ip_cache:
                self.ip_cache.append(address)
            try:
                header, date, name, message = data.decode('utf-8').split("\n\n",3)
                method = {
                    'LOGIN': self.login,
                    'REGISTER': self.register,
                    'MESSAGE': self.message,
                    'UPLOAD': self.upload,
                    'DOWNLOAD':self.download
                }
                method[header](date,name,message)
            except:
                print('ERROR')
                self.sock.sendto('ERROR\n\n'.encode('utf-8'),address)


    def login(self):
        pass

    def register(self):
        pass

    def message(self, date, name, message):
        print(f'{date}  {name}:{message}')
        for address in self.ip_cache:
            self.sock.sendto(f'{date}  {name}:{message}'.encode('UTF-8'), address)

        # TODO: SQL操作
        pass

    def upload(self):
        pass

    def download(self):
        pass

if __name__ == "__main__":
    service = Service()
    service.listen()