#!/usr/bin/env python3
import socket
import threading
import os
import sys
from hashlib import md5
from utilit import *
import time
import math


#SOURCEPATH = "/u1/h3/hashmi/public_html/source"
#SOURCEPATH = "/u1/h3/hashmi/public_html/sourceM10"
#SOURCEPATH = "/u1/h3/hashmi/public_html/sourceM"
SOURCEPATH = "/u1/h3/hashmi/public_html/sourceG"
os.chdir(SOURCEPATH)
CONCURR = 1     #sys.argv[1]

#list of source files
allfiles = os.listdir()
filesize = [os.stat(i).st_size for i in allfiles]

SERVER = "127.0.0.1"                 #SELECT HOME ADDR or GET MACHINE IP
#SERVER = "cs.indstate.edu"
#SERVER = socket.gethostbyaddr(socket.gethostname())[2][0]

#########################################################
# HEADER       # 116 bytes

PORT = 5050
SIZEl = 20
NAMEl = 50
CHECKSUMl = 32
FILEBLOCKl = 8
CURRl = 3
TOTALl = 3
TIDl = 2
HEADERSIZE = SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl+TOTALl+TIDl
#########################################################

filehash = md5()
PACKETSIZE = 128* filehash.block_size   #coz md5 has 128*64 digest blks

DATASIZE = PACKETSIZE - HEADERSIZE
qSize = 0
chunkByte = ''

locktx = [threading.Lock() for i in range(100)]
lockrx = [threading.Lock() for i in range(100)]

def txMutex(sock, buff,i):
    global locktx
    with locktx[i]:
        try:
            sock.sendall(buff)
        except:
            e = sys.exc_info()[0]
            print("EXCEPTION in writing")
            print(e)

def rxMutex(sock,i):
    global lockrx
    with lockrx[i]:
        buff = sock.recv(TIDl)
    return buff

class Transfer(threading.Thread):
    def __init__(self, Port ,Name, Size, Id, fid, totalf):
        threading.Thread.__init__(self)
        self.port = int(Port)
        self.fname = Name
        self.fsize = Size
        self.Tid = Id
        self.Fid = fid
        self.totalfiles = totalf
        self.data = ""
        with open(self.fname,"r") as fd:
            self.data = fd.read()
        #self.hash = md5()
        #with open(self.fname, "rb") as fd:
        #    for chunk in iter(lambda: fd.read(128*self.hash.block_size), b""):
        #        self.data = self.data.join

        print(f"Constructor end for t{self.Tid} filesize: {len(self.data)}")

    def run(self):
        global chunkByte
        packetCount = 1
        qEmptySpots = 3 #CONCURR
        srvMsg = ''
        HASH = md5sum(self.fname)
        print(f" t{self.Tid} GoT HASH : {HASH}")
        #with open(self.fname,"r") as fd:
        #    for chunk in iter(lambda: fd.read(DATASIZE), ""):
        for i in range(0,len(self.data),DATASIZE):
                chunk = self.data[i:i+DATASIZE]
                HEAD = f"{self.fsize:<{SIZEl}}{self.fname:<{NAMEl}}{HASH:<{CHECKSUMl}}{packetCount:<{FILEBLOCKl}}{self.Fid:<{CURRl}}{self.totalfiles:<{TOTALl}}{self.Tid:<{TIDl}}"
                #print(f"> t{self.Tid}, ",f"fileBlock: {packetCount}" )
                #print(HEAD)
                chunkByte = bytes(HEAD+chunk, 'utf-8')
                try:
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.connect((SERVER, self.port))
                    txMutex(client,chunkByte, self.Fid)
                    #client.sendall(chunkByte)
                    qEmptySpots -= 1
                except:
                    print(f"ERROR Tx for port:{self.port}\n")
                    e = sys.exc_info()
                    print(e)
                #srvMsg = rxMutex(client, self.Tid)
                #while True:
                    #srvMsg = client.recv(TIDl)
                #    srvMsg = int(srvMsg)
                #    print("current SERVER reply :",srvMsg, ", ",qEmptySpots)
                #    if srvMsg == self.Tid:
                #        qEmptySpots += 1
                #    if qEmptySpots >= 2:
                #        break
                client.close()
                #print(f"SERVER REPLY {srvMsg}, qEmptySpots:{qEmptySpots}")
                packetCount += 1
        print(f"file: {self.fname} Done reading\n")
        print(f"Thread END.  packetcount{packetCount}")
        #input()


if __name__ == '__main__':
    print(os.getcwd())
    print(f"number of files to read {len(allfiles)}")
    print(f"Client IP:{ socket.gethostbyaddr( socket.gethostname( )) }")
    threadCount = int(sys.argv[1])
    print(allfiles)

    transferthread = [0]*len(allfiles)
    #allfiles.pop(1)
    #filesize.pop(1)

    i = 0
    j  = 0

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))
    client.sendall(bytes(f"{threadCount:<20}", 'utf-8'))
    portList = client.recv(100).decode().split()
    portList = list(map(int, portList))
    print(portList)
    client.close()


    '''
    # for 1 file
    i = 0
    transferthread[i] = Transfer(portList[i], allfiles[i], filesize[i], j,i,len(allfiles))
    #transferthread[i] = Transfer(8060, allfiles[i], filesize[i], j,i,1)
    transferthread[i].start()
    print(f"> started thread 4 file {allfiles[i]}, thread count {threading.active_count()}")  #also includes Parent thread
    transferthread[i].join()
    '''
    if threadCount == 1:
        start = time.time()
        for i in range(len(allfiles)):
            transferthread[i] = Transfer(portList[0], allfiles[i], filesize[i], j,i,len(allfiles))
            transferthread[i].start()
            print(f"> started thread file: {allfiles[i]}, port:{portList[0]} thread count {threading.active_count()}")  #also includes Parent thread
            transferthread[i].join()

        stop = time.time()
        tot = stop - start
        totsum = 0
        for i in range(len(filesize)):
            totsum += filesize[i]

        print(f"Time taken:{tot} throughput for {len(allfiles)} files: {((totsum*100)/tot)/1000000} Mb/s ")

    else:
        s = '01234567'
        t = s[:threadCount]*(math.ceil(len(allfiles)/threadCount))
        t = t[:len(allfiles)]
    #tIndex = [t[i:i+threadCount] for i in range(0,len(t),threadCount)]
        print(t, f",  len(t)")
        #input()
        j = 0
        start = time.time()
        for i in t:
            k = int(i)
            transferthread[j] = Transfer(portList[k], allfiles[j], filesize[j], k,j,len(allfiles))
            transferthread[j].start()
            print(f"> started thread file: {allfiles[k]}, port:{portList[k]} thread count {threading.active_count()}")  #also includes Parent thread
            transferthread[j].join()
            j += 1

        stop = time.time()
        tot = stop - start
        totsum = 0
        for i in range(len(filesize)):
            totsum += filesize[i]
        print(f"Time taken:{tot} throughput for {len(allfiles)} files: {((totsum)/tot)/1000000} Mb/s ")







    print("DONE !!!!")

