#!/usr/bin/env python3
import socket
import os
import sys
from hashlib import md5



SOURCEPATH = "/u1/h3/hashmi/public_html/source"
os.chdir(SOURCEPATH)

#list of source files
allfiles = os.listdir()
filesize = [os.stat(i).st_size for i in allfiles]
filehash = md5()

SERVER = "127.0.0.1"                 #SELECT HOME ADDR or GET MACHINE IP
#SERVER = socket.gethostbyaddr(socket.gethostname())[2][0]

PORT = 8089
HEADERSIZE = 20
PACKETSIZE = 128* filehash.block_size   #coz md5 has 128*64 digest blks
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
#client.sendall(bytes("This is from Client",'UTF-8'))
print(os.getcwd())
print(f"number of files to read {len(allfiles)}")
i = 2
packetCount = 0


while True:
#for i in range(len(allfiles)):

    with open(allfiles[i],"r") as fd:
            HEAD = f"{filesize[i]:<{HEADERSIZE}}"
            msg = HEAD + fd.read(PACKETSIZE - HEADERSIZE)
            chunkByte = bytes(msg, 'utf-8')
            client.sendall(chunkByte)
            filehash.update(chunkByte)
            print(len(msg))
            for chunk in iter(lambda: fd.read(PACKETSIZE), ""):
                packetCount += 1
                chunkByte = bytes(chunk, 'utf-8')
                client.sendall(chunkByte)
                filehash.update(chunkByte)
    print("Done reading")
    HASH = filehash.hexdigest()
    print(HASH)
    client.sendall(bytes(HASH, 'utf-8'))
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
