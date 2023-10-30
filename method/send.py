import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
t = time.localtime()
date = f'{t.tm_year},{t.tm_mon},{t.tm_mday},{t.tm_hour}:{t.tm_min}:{t.tm_sec}'
name = 'shangxuwei'
try:
    msg = f"CHAT\n\n{date}\n\n{name}\n\n你好".encode('utf-8')
    sent = sock.sendto(msg, (ip, 10088))
    data, server = sock.recvfrom(4096)
    print(data.decode("utf-8"))
finally:
    sock.close()
