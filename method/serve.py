import socket

class Service:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 10088))


    def chat_listen(self):
        while True:
            data, address = self.sock.recvfrom(4096)
            header, message = data.decode('utf-8').split("\n\n",1)
            print(header,message)
            if data:
                self.sock.sendto('已接收到你发来的消息'.encode('UTF-8'), address)

    def message(self):
        pass

if __name__ == "__main__":
    service = Service()
    service.chat_listen()