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

class ChunkInfo():
    def __init__(self, chunkData, hashValue, peers):
        self.chunkData = chunkData  # Chunk data (e.g., bytes or a string)
        self.hashValue = hashValue  # Hash value of the chunk (e.g., string)
        self.peers = peers          # List of peers that contain this chunk

    def toDict(self):
        return {
            "chunkData": self.chunkData,
            "hashValue": self.hashValue,
            "peers": self.peers  # Assuming peers is a list of strings (peer addresses)
        }

class FileMetadata():
    def __init__(self,fileName,size):
        self.fileName = fileName
        self.size = size
    
    def chunkize(self,file,peerID):
        # chunk the file
        # self.chunkInfo = [] # index is chunkID, value is ??? chunk,hash??
        for i in range(1,10):
            chunkData = 1 # divide the file somehow 
            hashh = getHash(chunk)
            peers = [peerID]
            self.chunkInfo[i] = ChunkInfo(chunkData, hashh, peers)
    
    def toDict(self):
        return {
            "fileName": self.fileName
            "size": self.size
            "chunkInfo": [chunk.toDict() for chunk in self.ChunkInfo]
        }

    def addPeer(self,chunkID,peerID):
        self.chunkInfo[chunkID].peers.append(peerID)
