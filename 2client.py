#!/usr/bin/env python3
import socket
import os
import sys
from hashlib import md5
from md5sum import md5sum


SOURCEPATH = "/u1/h3/hashmi/public_html/source"
os.chdir(SOURCEPATH)

#list of source files
allfiles = os.listdir()
filesize = [os.stat(i).st_size for i in allfiles]
filehash = md5()

SERVER = "127.0.0.1"                 #SELECT HOME ADDR or GET MACHINE IP
#SERVER = socket.gethostbyaddr(socket.gethostname())[2][0]

PORT = 8089
SIZEl = 20              #20:filesize, 255:name, 32:CSum 168:EXTRA
NAMEl = 255
CHECKSUMl = 32
EXTRAl = 168
HEADERSIZE =  SIZEl+NAMEl+CHECKSUMl+EXTRAl

#HEADERSIZE = 20 + 255 + 200     #20:filesize, 255:name, 32:CSum 168:EXTRA
PACKETSIZE = 128* filehash.block_size   #coz md5 has 128*64 digest blks
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
#client.sendall(bytes("This is from Client",'UTF-8'))
print(os.getcwd())
print(f"number of files to read {len(allfiles)}")
i = 3

while True:
    packetCount = 0
    HASH = md5sum(allfiles[i])
    print(f"HASH : {HASH}")
    with open(allfiles[i],"r") as fd:
        HEAD = f"{filesize[i]:<20}{allfiles[i]:<255}{HASH:<200}"
        msg = HEAD + fd.read(PACKETSIZE - HEADERSIZE)
        chunkByte = bytes(msg, 'utf-8')
        client.sendall(chunkByte)
        print(len(msg))
        for chunk in iter(lambda: fd.read(PACKETSIZE), ""):
                packetCount += 1
                chunkByte = bytes(chunk, 'utf-8')
                client.sendall(chunkByte)
    print(f"{allfiles[i]} Done reading")
    print(HASH)
    input()

    '''
    print(lines)
    print("nunber of lines READED: ",len(lines))
    in_data =  client.recv(1024)
    print("From Server :" ,in_data.decode())
    out_data = input()
    client.sendall(lines )
    #client.sendall(bytes(lines,'UTF-8'))
    if out_data=='bye':
        break
    #i += 1
    '''
client.close()
