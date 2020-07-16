import socket

SERVER = "cs.indstate.edu"
PORT = 8089
threadCount = 1

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
client.sendall(bytes(f"{threadCount:<20}", 'utf-8'))
portList = client.recv(100).decode().split()
portList = list(map(int, portList))
print(portList)
client.close()




client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, 8090))



