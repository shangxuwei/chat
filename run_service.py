from service import  serve
import threading
import time

if __name__ == "__main__":
    service = serve.Service()
    listen = threading.Thread(target=service.listen)
    listen.daemon=True
    listen.start()
    while True:
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            print('service stopped')
            break