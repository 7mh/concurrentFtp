import sys
from hashlib import md5


def isPortInUse(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ex =  s.connect_ex(('localhost', port)) == 0
        return ex

def md5sum(filename):
    hash = md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(128 * hash.block_size), b""):
            hash.update(chunk)
    return hash.hexdigest()

if __name__ == '__main__':
    print(isPortInUse(8088))
