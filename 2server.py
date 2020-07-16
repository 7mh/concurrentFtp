#!/usr/bin/env python3

import socket
import threading
import os
from hashlib import md5
#from md5sum import md5sum
from utilit import *
import pdb


LOCALHOST = socket.gethostname()  #"127.0.0.1"
#LOCALHOST = socket.gethostbyaddr(socket.gethostname())[2][0]
PORT = 8089
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
SOURCEPATH = "/u1/h3/hashmi/public_html/dest"
os.chdir(SOURCEPATH)
CONCCUR = 1
#table = [{} for i in range(150)]
table = [[] for i in range(150)]
byteRecv = [0 for i in range(150)]

CsumPassed = 0
CsumFailed = 0

class ClientThread(threading.Thread):
    def __init__(self,clientAddress,clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        #print ("New connection added: ", clientAddress)

    def run(self):
        global CsumPassed, CsumFailed
        #print ("Connection from : ", clientAddress)
        #self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
        msg = ''
        new_msg = True
        count  = 1
        filesize = 0
        data = self.csocket.recv(PACKETSIZE)
        msg = data.decode()
        HEADER = msg[:HEADERSIZE]
        #print(f"HEADER !!! : {HEADER}")
        filesize = int(HEADER[:SIZEl])
        filename = HEADER[SIZEl: (SIZEl+NAMEl)].rstrip()
        filechksum = HEADER[(SIZEl+NAMEl):(SIZEl+NAMEl+CHECKSUMl)]
        fileblock = HEADER[(SIZEl+NAMEl+CHECKSUMl):(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl)].rstrip()
        currfile = HEADER[(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl):(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl)]
        totalfiles = HEADER[(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl):(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl+TOTALl)]
        clientThrdId = HEADER[(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl+TOTALl):(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl+TOTALl+TIDl)].rstrip()
        #print(f"> file size {filesize}, {filename},fileblock: {fileblock}, {filechksum}, currfile:{currfile}, tot:{totalfiles}, tid:{clientThrdId}")
        currfile = int(currfile)
        byteRecv[currfile] += len(msg) - HEADERSIZE

        #table[currfile][fileblock] = msg[HEADERSIZE:]
        table[currfile].append(msg[HEADERSIZE:])
        #print(f"- {byteRecv[currfile]} of {filesize}",msg[-40:])

        if byteRecv[currfile] == filesize:
            #try:
            with open(filename, 'a+') as fd:
                    for i in range(len(table[currfile])):
                        fd.write(table[currfile][i])
            #except:
            #    print("ERROR writing file on disk")
            chkSum = md5sum(filename)
            if filechksum == chkSum:
                print(f"> file size {filesize}, {filename},fileblock: {fileblock}, {filechksum}, currfile:{currfile}, tot:{totalfiles}, tid:{clientThrdId}")
                print(filename, ">>>>>>>>>>>>>>>> CHECKSUM PASSED !")
                #table[currfile].clear()
                CsumPassed += 1
            else:
                print(filename, ">>>>>>>>>CHECKSUM failED !")
                CsumFailed += 1
        self.csocket.send(bytes(clientThrdId,'UTF-8'))

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
        self.status = True
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.hostname, self.port))
        self.server.listen(2)

    def run(self):
        print("AT RUN FUNc")
        while self.status:
            #break
            print("at accept")
            clientsock, clientAddress = self.server.accept()
            print("Pased accept")
            self.csocket = clientsock
            self.threadJob()


    def threadJob(self):
        print("AT job !")

        global CsumPassed, CsumFailed
        #print ("Connection from : ", clientAddress)
        #self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
        msg = ''
        new_msg = True
        count  = 1
        filesize = 0
        data = self.csocket.recv(PACKETSIZE)
        msg = data.decode()
        HEADER = msg[:HEADERSIZE]
        #print(f"HEADER !!! : {HEADER}")
        filesize = int(HEADER[:SIZEl])
        filename = HEADER[SIZEl: (SIZEl+NAMEl)].rstrip()
        filechksum = HEADER[(SIZEl+NAMEl):(SIZEl+NAMEl+CHECKSUMl)]
        fileblock = HEADER[(SIZEl+NAMEl+CHECKSUMl):(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl)].rstrip()
        currfile = HEADER[(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl):(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl)]
        totalfiles = HEADER[(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl):(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl+TOTALl)]
        clientThrdId = HEADER[(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl+TOTALl):(SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl+TOTALl+TIDl)].rstrip()
        #print(f"> file size {filesize}, {filename},fileblock: {fileblock}, {filechksum}, currfile:{currfile}, tot:{totalfiles}, tid:{clientThrdId}")
        currfile = int(currfile)
        byteRecv[currfile] += len(msg) - HEADERSIZE

        #table[currfile][fileblock] = msg[HEADERSIZE:]
        table[currfile].append(msg[HEADERSIZE:])
        #print(f"- {byteRecv[currfile]} of {filesize}",msg[-40:])

        if byteRecv[currfile] == filesize:
            #try:
            with open(filename, 'a+') as fd:
                    for i in range(len(table[currfile])):
                        fd.write(table[currfile][i])
            #except:
            #    print("ERROR writing file on disk")
            chkSum = md5sum(filename)
            if filechksum == chkSum:
                print(f"> file size {filesize}, {filename},fileblock: {fileblock}, {filechksum}, currfile:{currfile}, tot:{totalfiles}, tid:{clientThrdId}")
                print(filename, ">>>>>>>>>>>>>>>> CHECKSUM PASSED !")
                #table[currfile].clear()
                CsumPassed += 1
            else:
                print(filename, ">>>>>>>>>CHECKSUM failED !")
                CsumFailed += 1
                print("byteRecv:",byteRecv,chkSum)
            self.status = False
        self.csocket.send(bytes(clientThrdId,'UTF-8'))
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
    print("thread count", threadCount)
    portList = getPortList(threadCount, PORT)
    clientsock.sendall(bytes(' '.join(portList), 'utf-8'))


    '''
    hostname = LOCALHOST
    port = 8090
    #print("AT RUN FUNT")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(server)
    #print("Server created !",server.connect_ex((hostname, port)), f"   port:{port}" )
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.server.settimeout(5.0)
    server.bind((LOCALHOST, 8090))
    server.listen(1)
    #print("Server closed ! ",server.connect_ex((hostname, port)) )
        #self.server.close()
    print("at accept")
    clientsock, clientAddress = server.accept()
    print("csocket = clientsock")

    '''
    server = [0 for i in range(threadCount)]


    for i in range(threadCount):
        server[i] = Server(LOCALHOST, int(portList[i] ))
        server[i].start()

        #server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #server.bind((LOCALHOST, PORT))
        #server.listen( 25 )
        #clientsock, clientAddress = server.accept()
        #threadCount = int(clientsock.recv(20))
        #clientsock.sendall(bytes(' '.join(portList), 'utf-8'))

