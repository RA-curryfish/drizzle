import socket
import json
from data_structures import *

SERVER_PORT = 99999
SERVER_NAME = "localhost"

locFileMetadataMap = dict() # dict of fileName to fileMetadata
globFileMetadataMap = dict() # dict of fileName to fileMetadata

############################
#Local functionality
############################


def getFileSize(fileName):
    # TODO implement
    return 0

def getFile(fileName):
    #TODO implement
    pass

def createFileMetadata(fileName, peerIP):
    fileMetadata = FileMetadata(fileName, getFileSize(fileName), peerIP, getFile(fileName))
    return fileMetadata

###########################
# Calls to server API
###########################

def registerNode(fileList):
    #Send register request to server - pass IP address, and file list
    #Get register status - success or failure
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerIP = socket.gethostname() #TODO client own IP, check
    #TODO check port to pass
    client_socket.connect((SERVER_NAME,SERVER_PORT))
    # file_data = [
    #     locFileMetadataList
    # ]
    for fileName in fileList:
        fileMetadata = createFileMetadata(fileName, peerIP)
        locFileMetadataMap[fileName] = fileMetadata
    request = Request("RegisterNode",(peerIP, locFileMetadataMap))
    client_socket.sendall(serialize(request))
    response = deserialize(client_socket.recv(2048))
    print(f"Response: status - {response.status}, body - {response.body}")

def getFileList():
    #Send get file list request to server
    #Get list of file names
    request = Request("GetFileList", tuple())
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
    # locFileMetadataList[fileName].chunkize(file)
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
