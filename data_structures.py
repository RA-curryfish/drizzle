# from typing import NameTuple
from collections import namedtuple

Request = namedtuple("Request", "reqType args")

def getHash(chunk):
    return 0

# class Request():
#     def __init__(self,reqType,args):
#         self.reqType = reqType
#         self.args = args

# class ChunkPeer():
#     def __init__(self,chunkID,peerList):
#         self.chunkID = chunkID
#         self.peerList = peerList

class FileMetadata():
    def __init__(self,fileName,size):
        self.fileName = fileName
        self.size = size
    
    def chunkize(file,peerID):
        # chunk the file
        self.chunkInfo = [] # index is chunkID, value is ??? chunk,hash??
        for i in range(1,10):
            chunk = 1 # divide the file somehow 
            self.chunkID
            self.chunkInfo[i].chunk = chunk
            self.chunkInfo[i].hash = getHash(chunk)
            self.chunkInfo[i].peerList.append(peerID)
    
    def addPeer(self,chunkID,peerID):
        self.chunkInfo[chunkID].peerList.append(peerID)
