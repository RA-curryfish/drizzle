import socket
import threading

from data_structures import *

SERVER_PORT = 9999
SERVER_NAME = "localhost"

peerList = [] # list of peers ??? needed???
fileList = [] # stores file list
fileMetadataMap = dict() #Filename(str) to FileMetadata object

def registerNode(peerID,clientfileMetadataMap):
    global peerList
    global fileList
    global fileMetadataMap
    peerList.append(peerID)
    fileList.extend(clientfileMetadataMap.keys())
    fileMetadataMap.update(clientfileMetadataMap)
    out = Response(ReqStatus.SUCCESS,None)
    return out

def getFileList():
    global fileList
    out = Response(ReqStatus.SUCCESS,fileList)
    return out

def getFileMetadata(fileName):
    global fileMetadataMap
    out = Response(ReqStatus.SUCCESS,fileMetadataMap[fileName])
    return out

def registerFile(fileMetaData, peerID):
    global fileMetadataMap
    fileMetadataMap[fileMetaData.fileName] = FileMetadata(fileMetaData.fileName, fileMetaData.size)
    for chunkInfo in fileMetaData.chunkInfo:
        registerChunk(fileMetaData.fileName,chunkInfo.chunkID, peerID)
    return Response(ReqStatus.SUCCESS,None)
    
def registerChunk(fileName,chunkID,peerID):
    #Return register status
    fileMetadataMap[fileName].addPeer(chunkID,peerID)
    return Response(ReqStatus.SUCCESS,None)

def processRequest(request):
    #Can be either:Register request, Get file lists, Get file info, Chunk register request
    out = None
    if (request.RequestType == RegisterNode):
        peerIP = request.Args[0]
        clientFileMetaDataMap = request.Args[1]
        assert( (peerIP is not None) and (clientFileMetaDataMap is not None))
        out = registerNode(peerIP,clientFileMetaDataMap)
        print(f"Registerd {peerIP}")
        print(f"Metadata {fileMetadataMap['abd']}")
    elif (request.RequestType == GetFileList):
        out = getFileList()
    elif (request.RequestType == GetFileMetadata):
        fileName = request.Args[0]
        assert(fileName is not None)
        out = getFileMetadata(fileName)
    elif (request.RequestType == RegisterChunk):
        fileName = request.Args[0]
        chunkID = request.Args[1]
        chunk = request.Args[2]
        out = registerChunk(fileName, chunkID, chunk)
    return out

def socket_target(conn):
    # TESTING ONLY
    # if(conn is None):
    #     filename = "bruh"
    #     clientip = "TESTIP"
    #     file = "A"*100
    #     tstFileMetadataMap = dict()
    #     tstFileMetadataMap[filename] = FileMetadata(filename,len(filename),clientip,file)
    #     data = Request(RegisterNode,[clientip,tstFileMetadataMap])
    #     reqser = serialize(data)
    #     reqdeser = deserialize(reqser)
    #     resp = processRequest(reqdeser)
    #     respser = serialize(resp)
    #     print(peerList[0])
    #     print(fileList[0])
    #     print(fileMetadataMap[filename].size)
    #     return
    # TESTING END
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
    print(f"SERVER ON {SERVER_NAME}:{SERVER_PORT}")
    ## TESTING ONLY
    # socket_target(None)
    ## TESTING END
    while True:

        client_socket, addr = server_socket.accept()
        print(f"Received req from client: {client_socket}, {addr}")
        threading.Thread(target = socket_target, args = [client_socket]).start()
        print("asdasdsadasdd")
    print("does not reach")

if __name__ == "__main__":
    initServer()