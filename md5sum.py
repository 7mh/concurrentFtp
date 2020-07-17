#!/usr/bin/env python

import sys
from hashlib import md5


def md5sum(filename):
    hash = md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(128 * hash.block_size), b""):
            hash.update(chunk)
    return hash.hexdigest()


def main():
    if len(sys.argv) < 2:
        print ("Usage: md5sum <filename>")
        exit()

    print (md5sum(sys.argv[1]))


if __name__ == "__main__":
    main()
