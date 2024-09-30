import socket
import json
from data_structures import *

SERVER_PORT = 99999
SERVER_NAME = "localhost"

locFileMetadataList = [] # list of fileMetadata
globFileMetadataList = [] # list of fileMetadata

# Calls to server API
def registerNode(fileList):
    #Send register request to server - pass IP address, and file list
    #Get register status - success or failure

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerIP = socket.gethostname() #TODO client own IP, check
    #TODO check port to pass
    client_socket.connect((SERVER_NAME,SERVER_PORT))
    file_data = [
        locFileMetadataList
    ]
    locFileNames = map(lambda x: x.fileName, locFileMetadataList)
    request = Request("RegisterNode",[peerID, locFileNames]) 

    for fileName in fileList:
        fileMetadata = FileMetadata(fileName, getFileSize(fileName), peerIP, getFile(fileName))
        chunkID = 0 
        for chunk in chunks:
            registerChunk(file,chunkID,chunk)
            chunkID += 1

def getFileList():
    #Send get file list request to server
    #Get list of file names
    request = Request("GetFileList", [])
    #encode request
    #send on socket
    # rcv bytes and populate globalFileList
    pass

def getFileMetadata(fileName):
    #Get the hosts and chunk info for each node where the file is present
    request = Request("GetFileMetadata", [fileName])
    pass

def registerChunk(fileName,chunkID):
    #Send filename and chunk ID
    #
    # send bytes on socket
    locFileMetadataList[fileName] = FileMetadata(fileName,getFileSize(fileName))
    locFileMetadataList[fileName].chunkize(file)
    for chunkInfo in locFileMetadataList[fileName].chunkInfo:
        chunk = chunkInfo.chunk
        chunkID = chunkInfo.chunkID
        request = Request("RegisterChunk",[fileName,chunkID,chunk])
    pass

def downloadChunk(fileName,chunkID):
    #send

    pass

def uploadChunk(fileName,chunkID):
    #send
    
    pass

def modifyChunk(fileName,chunkID):
    #Can we do this?    
    pass

def downloadFile():
    #get list of chunks from server
    #use rarest first to determine order of chunks
    #use multi-threading to download chunks parallely
    #once chunk is received, verify the chunk 
    pass

#Local functionality
def getFileSize(fileName):
    # TODO implement
    return 0

def getFile(fileName):
    #TODO implement
    pass