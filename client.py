#!/usr/bin/env python3
import socket
import os

SOURCEPATH = "/u1/h3/hashmi/public_html/source"
os.chdir(SOURCEPATH)

#list of source files
allfiles = os.listdir()
filesize = [os.stat(i).st_size for i in allfiles]

SERVER = "127.0.0.1"                    #HOME ADDR or GET MACHINE IP
#SERVER = socket.gethostbyaddr(socket.gethostname())[2][0]

PORT = 8089
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
#client.sendall(bytes("This is from Client",'UTF-8'))
print(os.getcwd())
print(f"number of files to read {len(allfiles)}")
i = 2
while True:

    try:
        with open(allfiles[i],"rb") as fd:
            lines = fd.read()
    except:
        print("ERROR Reading File !")

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
client.close()
