#!/usr/bin/env python3
import socket
import threading
import os
import sys
from hashlib import md5
from utilit import *
import time
import math
import subprocess

print("Usage $> 'client.py [ThreadCount]' \n")

#SOURCEPATH = "./sourceM10"
SOURCEPATH = "../sourceM"
#SOURCEPATH = "../sourceG"
#SOURCEPATH = "../sourceComb"

#Check if All data folders are there if not create
subprocess.run("./generateData.sh")

os.chdir(SOURCEPATH)
CONCURR = 1     #sys.argv[1]

#list of source files
allfiles = os.listdir()
filesize = [os.stat(i).st_size for i in allfiles]

#SERVER = "127.0.0.1"                 #SELECT HOME ADDR or GET MACHINE IP
#SERVER = "cs.indstate.edu"
SERVER = socket.gethostbyaddr(socket.gethostname())[2][0]

PORT = 5090
#########################################################
# HEADER       # 118 bytes

SIZEl = 20          #file size
NAMEl = 50          #file name
CHECKSUMl = 32      #checksum
FILEBLOCKl = 8      #file block
CURRl = 3           #currnt file index
TOTALl = 3          #total files
TIDl = 2            #thread id
HEADERSIZE = SIZEl+NAMEl+CHECKSUMl+FILEBLOCKl+CURRl+TOTALl+TIDl
#########################################################

filehash = md5()
PACKETSIZE = 128* filehash.block_size   #coz md5 has 128*64 digest blks

DATASIZE = PACKETSIZE - HEADERSIZE
qSize = 0
chunkByte = ''

locktx = [threading.Lock() for i in range(len(allfiles))]
lockrx = [threading.Lock() for i in range(len(allfiles))]

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

        print(f"Constructor end for t{self.Tid} filesize: {len(self.data)}")

    def run(self):
        global chunkByte
        packetCount = 1
        qEmptySpots = 3 #CONCURR
        srvMsg = ''
        HASH = md5sum(self.fname)
        print(f" t{self.Tid} GoT HASH : {HASH}")
        for i in range(0,len(self.data),DATASIZE):
                chunk = self.data[i:i+DATASIZE]
                HEAD = f"{self.fsize:<{SIZEl}}{self.fname:<{NAMEl}}{HASH:<{CHECKSUMl}}{packetCount:<{FILEBLOCKl}}{self.Fid:<{CURRl}}{self.totalfiles:<{TOTALl}}{self.Tid:<{TIDl}}"
                #print(f"> t{self.Tid}, ",f"fileBlock: {packetCount}" )
                chunkByte = bytes(HEAD+chunk, 'utf-8')
                try:
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.connect((SERVER, self.port))
                    txMutex(client,chunkByte, self.Fid)
                    qEmptySpots -= 1
                except:
                    print(f"ERROR Tx for port:{self.port}\n")
                    e = sys.exc_info()
                    print(e)
                #srvMsg = rxMutex(client, self.Tid)
                srvMsg = client.recv(TIDl)
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
    if len(sys.argv) == 1:
        threadCount = 1
    else:
        threadCount = int(sys.argv[1])
    print(allfiles)

    transferthread = [0]*len(allfiles)


    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))
    client.sendall(bytes(f"{threadCount:<20}", 'utf-8'))
    portList = client.recv(100).decode().split()
    portList = list(map(int, portList))
    print(portList)
    client.close()

    s = '0123456789'
    t = s[:threadCount]*(math.ceil(len(allfiles)/threadCount))
    t = t[:len(allfiles)]
    print(t, f",  len(t)")
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

