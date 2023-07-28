import os
import questionary as qy

import detect_uid
import signup

from httpserver import Server
import threading

def main():
    server = Server(12345)
    detect = threading.Thread(target=detect_uid.main, daemon=True)
    detect.start()
    while True:
        try:
            server.listen()
        except KeyboardInterrupt:
            print('\nAbort.')
            break
    detect.join()

if __name__ == '__main__':
    main()
    