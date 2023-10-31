import socket

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
                method = {
                    'LOGIN': self.login,
                    'REGISTER': self.register,
                    'MESSAGE': self.message,
                    'UPLOAD': self.upload,
                    'DOWNLOAD':self.download
                }
                method[header](date,name,payload)
            except:
                print(data.decode('utf-8'))
                print('ERROR')
                self.sock.sendto('ERROR\n\n \n\n \n\n '.encode('utf-8'),address)


    def login(self):
        pass

    def register(self):
        pass

    def message(self, date, name, payload):
        print(f'{date}  {name}:{payload}')
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