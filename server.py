import socket
import threading

from data_structures import *

SERVER_PORT = 99999
SERVER_NAME = "localhost"

peerList = [] # list of peers ??? needed???
fileList = [] # stores file list
fileMetadataList = dict() #Filename(str) to FileMetadata object

def registerNode(peerID,localFileList):
    #REturn register status - success or failure
    peerList.append(peerID)
    fileList.append(localFileList)
    return ReqStatus.SUCCESS

def getFileList():
    #REturn list of file names
    return fileList

def getFileMetadata(fileName):
    #REturn the hosts and chunk info for each node where the file is present
    return fileMetadataList[fileName]

def registerFile(fileMetaData, peerID):
    # recieves file meta data
    fileMetadataList[fileMetaData.fileName] = FileMetadata(fileMetaData.fileName, fileMetaData.size)
    for chunkInfo in fileMetaData.chunkInfo:
        registerChunk(fileMetaData.fileName,chunkInfo.chunkID, peerID)
    return ReqStatus.SUCCESS
    
def registerChunk(fileName,chunkID,peerID):
    #Return register status
    fileMetadataList[fileName].addPeer(chunkID,peerID)
    return ReqStatus.SUCCESS

def processRequest(request):
    #Get request type
    #Can be either:
        #Register request
        #Get file lists
        #Get file info
        #Chunk register request
    #TODO call the appropriate fn and do marshalling
    # request = pickl
    out = None
    # serializedOut = pickle.dumps(out) 
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