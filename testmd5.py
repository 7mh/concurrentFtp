import sys
import os
from hashlib import md5

def md5sum(filename):
    hash = md5()
    with open(filename, "r") as f:
        for chunk in iter(lambda: f.read(128 * hash.block_size), ""):
            hash.update(bytes(chunk, 'utf-8'))
    return hash.hexdigest()



SOURCEPATH = "/u1/h3/hashmi/public_html/source"
os.chdir(SOURCEPATH)

h= md5()
allfiles = os.listdir()
count = 0
with open(allfiles[2], "r") as fd:
    for c in iter(lambda: fd.read(128*h.block_size),""):
        print(type(c), len(c))
        count += 1
        bytec = bytes(c,'utf-8')
        h.update(bytec)
print(h.hexdigest())
