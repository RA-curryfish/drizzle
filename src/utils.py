# from typing import NameTuple
from collections import namedtuple, OrderedDict
from enum import Enum
import hashlib
import codecs
import pickle
import logging
import sys

logging.basicConfig(level=logging.INFO)
# logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

####################################
# Defining constants and classes   #
####################################

# Request type values
RegisterNode = "RegisterNode"
GetFileList = "GetFileList"
GetFileMetadata = "GetFileMetadata"
RegisterChunk = "RegisterChunk"

# Server info
SERVER_PORT = 55555
SERVER_NAME = "130.203.16.40"

# Chunk size
CHUNK_SIZE = 128

# Request status
class ReqStatus(Enum):
    SUCCESS = 0
    FAILURE = 1

# Generates and retursn hash using SHA1
def getHash(chunk):
    return hashlib.sha1(chunk).hexdigest() 

# Serializer for the bytes to be sent over the network
def serialize(obj): #Input object, return bytes
    return codecs.encode(pickle.dumps(obj), "base64")

# Deserializes the bytes sent over the network back into object 
def deserialize(serText): #Input bytes, return object
    return pickle.loads(codecs.decode(serText, "base64"))

# Helper to print progress bar
def printProgressBar(index, total, label):
    n_bar = 50  # Progress bar width
    progress = index / total
    # sys.stdout.write('\r')
    # sys.stdout.write(f"[{'=' * int(n_bar * progress):{n_bar}s}] {int(100 * progress)}%  {label}")
    # sys.stdout.flush()
    logging.info(f"[{'=' * int(n_bar * progress):{n_bar}s}] {int(100 * progress)}%  {label}")

# Class for request with request type and list of arguments
class Request():
    def __init__(self,reqType,args):
        self.RequestType = reqType
        self.Args = args

# Class for response with status and a body
class Response():
    def __init__(self,stat,body):
        self.Status = stat
        self.Body = body

# Class for chunk information containing hash value and list of peers
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

# Class for file metadata containing filename, file size, and list of chunkinfo objects
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