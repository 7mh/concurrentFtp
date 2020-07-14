#!/usr/bin/env python3

import socket
import threading
import os
from hashlib import md5
import md5sum


LOCALHOST = "127.0.0.1"
#LOCALHOST = socket.gethostbyaddr(socket.gethostname())[2][0]
PORT = 8089
HEADERSIZE = 20
filehash = md5()
PACKETSIZE = 128* filehash.block_size   #coz md5 has 128*64 digest blks
SOURCEPATH = "/u1/h3/hashmi/public_html/dest"
os.chdir(SOURCEPATH)


'''
def md5sum(filename):
    hash = md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(128 * hash.block_size), b""):
            hash.update(chunk)
    return hash.hexdigest()
'''

class ClientThread(threading.Thread):
    def __init__(self,clientAddress,clientsocket, num):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        self.filenum = str(num)
        print ("New connection added: ", clientAddress)

    def run(self):
        print ("Connection from : ", clientAddress)
        #self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
        msg = ''
        new_msg = True
        count  = 1
        byteRecv = 0
        try:
            fd = open(self.filenum, 'a+')
        except:
            print("ERROR OPENING FILE")

        while True:
            data = self.csocket.recv(PACKETSIZE)
            msg = data.decode()
            if len(msg) < PACKETSIZE:
                print(msg[:100])
                print(msg[-100:])
            if new_msg == False:
                byteRecv += len(msg)
                fd.write(msg)
            if new_msg:
                filesize = int(msg[:HEADERSIZE])
                print(f"new file size {filesize}")
                byteRecv = len(msg) - HEADERSIZE
                fd.write(msg[HEADERSIZE:])
                new_msg = False
            print (f"{count} read from client LEN:{len(msg)} RECV:{byteRecv}", msg[:40])
            count += 1
            #if msg=='bye':
            if len(msg) == 0:               #when client closes socket
                print("RECVD empty msg")
                break

            #if byteRecv >= filesize :       #Paranioa
            #    break

            if (byteRecv + PACKETSIZE) >= filesize :
                data = self.csocket.recv(PACKETSIZE)
                msg = data.decode()
                left = filesize - byteRecv
                print(f"LAST MSG {len(msg)}")
                print(msg[:left])             # write it on disk
                fd.write(msg[:left])

                print(msg[(left): (left +32)])
                HASH = msg[(left): (left +32)]
                print("HASH is: ",HASH)
                break

                #print(msg[:left])

            #self.csocket.send(bytes(msg,'UTF-8'))

        print ("Client at ", clientAddress , " disconnected...")
        self.csocket.close()
        fd.close()


if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LOCALHOST, PORT))
    print("Server started")
    print("Waiting for client request..")
    num = 1
    while True:
        server.listen(1)
        clientsock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientsock,num)
        num += 1
        newthread.start()
