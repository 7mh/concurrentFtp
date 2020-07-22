#!/usr/bin/env python3

import socket
import threading
import os
from hashlib import md5
from utilit import *
import pdb
import subprocess


#LOCALHOST = '127.0.0.1'
LOCALHOST = socket.gethostname()  #"127.0.0.1"
#LOCALHOST = socket.gethostbyaddr(socket.gethostname())[2][0]
PORT = 5090
MAXFILES = 150
#HEADERSIZE = 20
###############################################################
SIZEl = 20              #20:filesize, 50:name, 32:CSum 8:EXTRA
NAMEl = 50
CHECKSUMl = 32
FILEBLOCKl = 8
TIDl = 2
CURRl = 3
TOTALl = 3
HEADERSIZE =  SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl+TOTALl+TIDl
###############################################################
filehash = md5()
PACKETSIZE = 128* filehash.block_size   #coz md5 has 128*64 digest blks

subprocess.run('./checkDest.sh')
SOURCEPATH = "./dest"
os.chdir(SOURCEPATH)
CONCCUR = 1
table = [[] for i in range(MAXFILES)]
byteRecv = [0 for i in range(MAXFILES)]

CsumPassed = 0
CsumFailed = 0


def getPortList(tcount, currPort):
    ports = []
    i = 0
    currPort += 1
    while i < tcount:
        if isPortInUse(currPort) == 0:
            ports.append(str(currPort))
        i += 1
        currPort += 1
        print(ports)
    return ports

class Server(threading.Thread):
    def __init__(self, hostname, port):
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.hostname, self.port))
        self.server.listen(10)

    def run(self):
        print("AT RUN FUNc")
        while True:
            clientsock, clientAddress = self.server.accept()
            self.csocket = clientsock
            self.threadJob()


    def threadJob(self):

        global CsumPassed, CsumFailed, table, byteRecv
        msg = ''
        new_msg = True
        count  = 1
        filesize = 0
        data = self.csocket.recv(PACKETSIZE)
        msg = data.decode()
        HEADER = msg[:HEADERSIZE]
        filesize = int(HEADER[:SIZEl])
        filename = HEADER[SIZEl: (SIZEl+NAMEl)].rstrip()
        filechksum = HEADER[(SIZEl+NAMEl):(SIZEl+NAMEl+CHECKSUMl)]
        fileblock = HEADER[(SIZEl+NAMEl+CHECKSUMl):(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl)].rstrip()
        currfile = HEADER[(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl):(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl)]
        totalfiles = HEADER[(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl):(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl+TOTALl)]
        clientThrdId = HEADER[(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl+TOTALl):(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl+TOTALl+TIDl)].rstrip()


        currfile = int(currfile)
        byteRecv[currfile] += len(msg) - HEADERSIZE

        table[currfile].append(msg[HEADERSIZE:])

        if byteRecv[currfile] == filesize:
            with open(filename, 'a+') as fd:
                    for i in range(len(table[currfile])):
                        fd.write(table[currfile][i])
            chkSum = md5sum(filename)
            if filechksum == chkSum:
                print(f"> file size {filesize}, {filename},fileblock: {fileblock}, {filechksum}, currfile:{currfile}, tot:{totalfiles}, tid:{clientThrdId}")
                table[currfile].clear()
                CsumPassed += 1
                print(filename, ">>>>>>>>>>>>>>>> CHECKSUM PASSED !",CsumPassed, f"len table:{len(table[currfile])}\n")
            else:
                print(filename, ">>>>>>>>>CHECKSUM failED !")
                CsumFailed += 1
                print("byteRecv:",byteRecv,chkSum)
        return

if __name__ == "__main__":

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(s.connect_ex((LOCALHOST, PORT)))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LOCALHOST, PORT))
    server.listen( 1 )
    print(f"Server started at {LOCALHOST}")
    print("Waiting for client request..")

    clientsock, clientAddress = server.accept()
    threadCount = int(clientsock.recv(20))
    print("thread count", threadCount, f"Client at : {clientAddress}")
    portList = getPortList(threadCount, PORT)
    clientsock.sendall(bytes(' '.join(portList), 'utf-8'))


    server = [0 for i in range(threadCount)]


    for i in range(threadCount):
        server[i] = Server(LOCALHOST, int(portList[i] ))
        server[i].start()

