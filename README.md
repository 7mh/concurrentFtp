# Concurrent File Transfer
 A concurrent file transfer app. <br/>
 The goal of this project is to create a multi-threaded version of "rsync".
 
 Transfer validation is acheived by calculating MD5 checksum before and after transfer. 
 

## Prerequisite
Python3 

## HOW TO Run

### 1. Setup receiving server
Run `server.py` to setup receiving server.

### 2. Start client

CLI Usage $> 'client.py [ThreadCount]
Run `client.py [ThreadCount]` to start transfering data to server.


#### To clone this repository.

run " git clone git@github.com:7mh/concurrentFtp.git "


<br/><br/>
Note: When running on default global values of `client.py`. It generates dataset first and then transfer those data files. Modify "SOURCE" in `client.py`


