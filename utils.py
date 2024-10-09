# from typing import NameTuple
from collections import namedtuple, OrderedDict
from enum import Enum
import hashlib
import codecs
import pickle
import logging
import sys

logging.basicConfig(level=logging.DEBUG)
# logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
# Request type values
RegisterNode = "RegisterNode"
GetFileList = "GetFileList"
GetFileMetadata = "GetFileMetadata"
RegisterChunk = "RegisterChunk"

SERVER_PORT = 55555
SERVER_NAME = "130.203.16.40"

CHUNK_SIZE = 20

class ReqStatus(Enum):
    SUCCESS = 0
    FAILURE = 1

def getHash(chunk):
    return hashlib.sha1(chunk).hexdigest() 

def serialize(obj): #Input object, return bytes
    return codecs.encode(pickle.dumps(obj), "base64")

def deserialize(serText): #Input bytes, return object
    return pickle.loads(codecs.decode(serText, "base64"))

def printProgressBar(index, total, label):
    n_bar = 50  # Progress bar width
    progress = index / total
    # sys.stdout.write('\r')
    # sys.stdout.write(f"[{'=' * int(n_bar * progress):{n_bar}s}] {int(100 * progress)}%  {label}")
    # sys.stdout.flush()
    logging.info(f"[{'=' * int(n_bar * progress):{n_bar}s}] {int(100 * progress)}%  {label}")

class Request():
    def __init__(self,reqType,args):
        self.RequestType = reqType
        self.Args = args

class Response():
    def __init__(self,stat,body):
        self.Status = stat
        self.Body = body

class ChunkInfo():
    # def __init__(self, chunkData, hashValue, peers):
    def __init__(self, hashValue, peers):
        # self.chunkData = chunkData  # Chunk data (e.g., bytes or a string)
        self.hashValue = hashValue  # Hash value of the chunk (e.g., string)
        self.peers = peers          # List of peers that contain this chunk

    def toDict(self):
        return {
            # "chunkData": self.chunkData,
            "hashValue": self.hashValue,
            "peers": self.peers  # Assuming peers is a list of strings (peer addresses)
        }

class FileMetadata():
    def __init__(self,fileName,size,peerId,peerPort,filePath):
        self.fileName = fileName
        self.size = size
        self.chunkInfo = []
        with open(filePath,"rb") as fh:
            for i in range(0, size, CHUNK_SIZE): #
                chunkData = fh.read(CHUNK_SIZE)
                hashh = getHash(chunkData)
                peers = [(peerId, peerPort)]
                # self.chunkInfo.append(ChunkInfo(chunkData, hashh, peers))
                self.chunkInfo.append(ChunkInfo(hashh, peers))
    
    def toDict(self):
        return {
            "fileName": self.fileName,
            "size": self.size,
            "chunkInfo": [chunk.toDict() for chunk in self.chunkInfo]
        }
    def __str__(self):
        return str(self.toDict())
    def addPeer(self,chunkID,peerID,peerPort):
        self.chunkInfo[chunkID].peers.append((peerID,peerPort))