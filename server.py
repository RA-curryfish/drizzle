import socket
import threading

from data_structures import *

SERVER_PORT = 99999
SERVER_NAME = "localhost"

peerList = [] # list of peers ??? needed???
fileList = [] # stores file list
fileMetadataMap = dict() #Filename(str) to FileMetadata object

def registerNode(peerID,clientfileMetadataMap):
    global peerList
    global fileMetadataMap
    peerList.append(peerID)
    fileMetadataMap.update(clientfileMetadataMap)
    return ReqStatus.SUCCESS

def getFileList():
    global fileList
    return fileList

def getFileMetadata(fileName):
    global fileMetadataMap
    return fileMetadataMap[fileName]

def registerFile(fileMetaData, peerID):
    global fileMetadataMap
    fileMetadataMap[fileMetaData.fileName] = FileMetadata(fileMetaData.fileName, fileMetaData.size)
    for chunkInfo in fileMetaData.chunkInfo:
        registerChunk(fileMetaData.fileName,chunkInfo.chunkID, peerID)
    return ReqStatus.SUCCESS
    
def registerChunk(fileName,chunkID,peerID):
    #Return register status
    fileMetadataMap[fileName].addPeer(chunkID,peerID)
    return ReqStatus.SUCCESS

def processRequest(request):
    #Get request type
    #Can be either:
        #Register request, Get file lists, Get file info, Chunk register request
    out = None

    if (request.RequestType == RegisterNode):
        peerIP = request.Args[0]
        clientFileMetaDataMap = request.Args[1]
        assert( (peerIP is not None) and (clientFileMetaDataMap is not None))
        out = RegisterNode(peerIP,clientFileMetaDataMap)
    elif (request.RequestType == GetFileList):
        out = GetFileList()
    elif (request.RequestType == GetFileMetadata):
        fileName = request.Args[0]
        assert(fileName is not None)
        out = GetFileMetadata(fileName)
    elif (request.RequestType == RegisterChunk):
        fileName = request.Args[0]
        chunkID = request.Args[1]
        chunk = request.Args[2]
        out = RegisterChunk(fileName, chunkID, chunk)
    return out

def socket_target(conn):
    serializedReq = bytearray()
    while True: 
        data = conn.recv(1024) 
        if not data: 
            break
        serializedReq.extend(data)
    serializedReq = bytes(serializedReq)
    request = deserialize(serializedReq)
    reqResponse = processRequest(request)
    serializedResp = serialize(reqResponse)
    conn.send(serializedResp)

def initServer():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_NAME,SERVER_PORT))
    server_socket.listen(10) #Max 10 peers in the queue
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Received req from client: {client_socket}, {addr}")
        threading.Thread(target = socket_target, args = client_socket).start

if __name__ == "__main__":
    initServer()