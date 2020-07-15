#!/usr/bin/env python3
import socket
import threading
import os
import sys
from hashlib import md5
from md5sum import md5sum


SOURCEPATH = "/u1/h3/hashmi/public_html/source"
os.chdir(SOURCEPATH)
CONCURR = 1     #sys.argv[1]

#list of source files
allfiles = os.listdir()
filesize = [os.stat(i).st_size for i in allfiles]

SERVER = "cs.indstate.edu"                 #SELECT HOME ADDR or GET MACHINE IP
#SERVER = socket.gethostbyaddr(socket.gethostname())[2][0]

#########################################################
# HEADER       # 116 bytes

PORT = 8089
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

class Transfer(threading.Thread):
    def __init__(self, serverAddr, seversocket, Name, Size, Id, fid, totalf):
        threading.Thread.__init__(self)
        self.fname = Name
        self.fsize = Size
        self.Tid = Id
        self.Fid = fid
        self.totalfiles = totalf
        print(f"Constructor end for t{self.Tid}")

    def run(self):
        packetCount = 1
        qEmptySpots = 3 #CONCURR
        srvMsg = ''
        HASH = md5sum(self.fname)
        print(f" t{self.Tid} GoT HASH : {HASH}")
        with open(self.fname,"r") as fd:
            for chunk in iter(lambda: fd.read(DATASIZE), ""):
                HEAD = f"{self.fsize:<{SIZEl}}{self.fname:<{NAMEl}}{HASH:<{CHECKSUMl}}{packetCount:<{FILEBLOCKl}}{self.Fid:<{CURRl}}{self.totalfiles:<{TOTALl}}{self.Tid:<{TIDl}}"
                print(f"> t{self.Tid}, ",len(HEAD)+len(chunk))
                chunkByte = bytes(HEAD+chunk, 'utf-8')
                try:
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.connect((SERVER, PORT))
                    client.sendall(chunkByte)
                    qEmptySpots -= 1
                except:
                    print(f"ERROR Tx for t{self.Tid}")
                while True:
                    srvMsg = client.recv(64)
                    srvMsg = int(srvMsg)
                    print("current SERVER reply :",srvMsg, ", ",qEmptySpots)
                    if srvMsg == self.Tid:
                        qEmptySpots += 1
                    if qEmptySpots >= 2:
                        break
                client.close()
                print(f"SERVER REPLY {srvMsg}, qEmptySpots:{qEmptySpots}")
                packetCount += 1
        print(f"{self.fname} Done reading\n")
        print(HASH, f"packetcount{packetCount}")
        #input()


#client.sendall(bytes("This is from Client",'UTF-8'))
if __name__ == '__main__':
    print(os.getcwd())
    print(f"number of files to read {len(allfiles)}")
    #client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    #UNDO Maybe
    client = 1
    #allfiles.pop(2)
    #filesize.pop(2)
    #i = 2
    for i in range(len(allfiles)):
    #while True:
        transferthread = Transfer(SERVER, client ,allfiles[i], filesize[i], 1,i, len(allfiles))
        print(f"started thread {i}")
        transferthread.start()

        #input()

