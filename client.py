import socket
import json

SERVER_PORT = 99999
SERVER_NAME = "localhost"

def getFileSize(fileName):
    return 0

def registerNode(fileList):
    #Send register request to server - pass IP address, and file list
    #Get register status - success or failure

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerID = socket.gethostname()
    client_socket.connect((SERVER_NAME,SERVER_PORT))
    file_data = [
        locFileMetadataList
    ]
    request = Request("RegisterNode",[peerID, locFileMetadataList.keys()]) 

    for file in fileList:
        chunks = chunkize(file)
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
    pass

def downloadFile():
    #get list of chunks from server
    #use rarest first to determine order of chunks
    #use multi-threading to download chunks parallely
    #once chunk is received, verify the chunk 
    pass

locFileMetadataList = [] # list of fileMetadata
globFileMetadataList = [] # list of fileMetadata