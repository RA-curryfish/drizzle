# from typing import NameTuple
from collections import namedtuple
from enum import Enum
import hashlib
import codecs
import pickle

CHUNK_SIZE = 1024

Request = namedtuple("RequestType", "Args")
Response = namedtuple("Status", "Body")

class ReqStatus(Enum):
    SUCCESS = 0
    FAILURE = 1

def getHash(chunk):
    return hashlib.sha1(str.encode()).hexdigest() 

def serialize(obj): #Input object, return bytes
    return codecs.encode(pickle.dumps(obj), "base64")

def deserialize(serText): #Input bytes, return object
    return pickle.loads(codecs.decode(serText, "base64"))

# class Request():
#     def __init__(self,reqType,args):
#         self. Type = reqType
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
    def __init__(self,fileName,size,peerId,file):
        self.fileName = fileName
        self.size = size
        self.chunkInfo = []
        for i in range(0, size, CHUNK_SIZE): #
            chunkData = file[i*CHUNK_SIZE:(i+1)*CHUNK_SIZE] # TODO divide the file somehow 
            hashh = getHash(chunkData)
            peers = [peerId]
            self.chunkInfo.append(ChunkInfo(chunkData, hashh, peers))
    
    def toDict(self):
        return {
            "fileName": self.fileName,
            "size": self.size,
            "chunkInfo": [chunk.toDict() for chunk in self.ChunkInfo]
        }

    def addPeer(self,chunkID,peerID):
        self.chunkInfo[chunkID].peers.append(peerID)

def 
