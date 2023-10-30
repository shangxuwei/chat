import socket

class Service:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 10088))
        self.ip_cache = []

    def chat_listen(self):
        while True:
            data, address = self.sock.recvfrom(4096)
            if address not in self.ip_cache:
                self.ip_cache.append(address)
            header, date, name, message = data.decode('utf-8').split("\n\n",3)
            method = {
                'LOGIN': self.login,
                'REGISTER': self.register,
                'CHAT': self.chat,
                'UPLOAD': self.upload,
                'DOWNLOAD':self.download
            }
            method[header](date,name,message)
            if data:
                # self.sock.sendto(f'{date}  {name}:{message}'.encode('UTF-8'), address)
                pass
    def login(self):
        pass
    def register(self):
        pass
    def chat(self, date, name, message):
        print(f'{date}  {name}:{message}')
        for address in self.ip_cache:
            self.sock.sendto(f'{date}  {name}:{message}'.encode('UTF-8'), address)
        pass
    def upload(self):
        pass
    def download(self):
        pass

if __name__ == "__main__":
    service = Service()
    service.chat_listen()