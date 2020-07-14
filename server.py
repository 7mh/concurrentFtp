#!/usr/bin/env python3

import socket
import threading
import os
from hashlib import md5
from md5sum import md5sum
import pdb


LOCALHOST = "127.0.0.1"
#LOCALHOST = socket.gethostbyaddr(socket.gethostname())[2][0]
PORT = 8089
#HEADERSIZE = 20
SIZEl = 20              #20:filesize, 255:name, 32:CSum 168:EXTRA
NAMEl = 255
CHECKSUMl = 32
EXTRAl = 168
HEADERSIZE =  SIZEl+NAMEl+CHECKSUMl+EXTRAl
filehash = md5()
PACKETSIZE = 128* filehash.block_size   #coz md5 has 128*64 digest blks
SOURCEPATH = "/u1/h3/hashmi/public_html/dest"
os.chdir(SOURCEPATH)


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
        filesize = 0
        try:
            fd = open(self.filenum, 'a+')
        except:
            print("ERROR OPENING FILE")

        while True:
            #condition when a small file occupies only 1 Packet
            if byteRecv != 0 and filesize != 0 and byteRecv >= filesize:
                break

            data = self.csocket.recv(PACKETSIZE)
            msg = data.decode()


            if new_msg == False:
                byteRecv += len(msg)
                fd.write(msg)
                if len(msg) == 0:               #when client closes socket
                    print("RECVD empty msg")
                    break
                if byteRecv >= filesize:
                    print("Transfer complete")
                    break
            if new_msg:
                HEADER = msg[:HEADERSIZE]
                print(f"HEADER : {HEADER}")
                filesize = int(HEADER[:SIZEl])
                filename = HEADER[SIZEl: (SIZEl+NAMEl)]
                filechksum = HEADER[(SIZEl+NAMEl):(SIZEl+NAMEl+32)]

                print(f"new file size {filesize}, {filename}, {filechksum}")
                byteRecv = len(msg) - HEADERSIZE
                fd.write(msg[HEADERSIZE:])
                new_msg = False
            print (f"{count} read from client LEN:{len(msg)} RECV:{byteRecv}", msg[:40])
            count += 1
            #if len(msg) < PACKETSIZE:   #testing
            #    break
            #if msg=='bye':

            #if byteRecv >= filesize :       #Paranioa
            #    break
            '''
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
            '''
                #print(msg[:left])

            #self.csocket.send(bytes(msg,'UTF-8'))

        print ("Client at ", clientAddress , " disconnected...")
        self.csocket.close()
        fd.close()
        filename = filename.rstrip()
        os.rename(self.filenum, filename)
        chkSum = md5sum(filename)
        #print(chkSum, filechksum == chkSum)
        #pdb.set_trace()
        if filechksum == chkSum:
            print(filename, "CHECKSUM PASSED !")
        else:
            print(filename, "CHECKSUM failED !")


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
