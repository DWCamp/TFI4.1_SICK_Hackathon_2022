"""
Try to receive IP broadcast from Safelog AGV
"""

from socket import *


def main():
    import socket
    UDP_IP = "127.0.0.1"
    UDP_PORT = 8900

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        print("received message: %s" % data)



if __name__ == '__main__':
    main()
