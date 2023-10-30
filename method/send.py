import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    msg = "chat\n\n 你好".encode('utf-8')
    sent = sock.sendto(msg, ('10.106.187.124', 10088))
    data, server = sock.recvfrom(4096)
    print(data.decode())
finally:
    sock.close()
