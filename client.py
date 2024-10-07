import socket
from data_structures import *
import threading
import os
import sys

SERVER_PORT = 55555
SERVER_NAME = "130.203.16.40"
CLIENT_IP = socket.gethostbyname(socket.gethostname())
CLIENT_PORT = None
FILES_DIR = ""

locFileMetadataMap = dict() # dict of fileName to fileMetadata
globFileList = list() 
globFileMetadata = dict() # dict of fileName to fileMetadata

############################
#Local functionality
############################
def getFilePath(fileName):
    return FILES_DIR+"/"+fileName

def getFileSize(fileName):
    return os.path.getsize(getFilePath(fileName))

def createFileMetadata(fileName):
    fileMetadata = FileMetadata(fileName, getFileSize(fileName), CLIENT_IP, CLIENT_PORT, getFilePath(fileName))
    return fileMetadata

def sendReqToServer(request):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connecting to server: {SERVER_NAME, SERVER_PORT}")
    client_socket.connect((SERVER_NAME,SERVER_PORT))
    client_socket.sendall(serialize(request))
    client_socket.shutdown(socket.SHUT_WR)
    response = bytearray()
    while True:
        data = client_socket.recv(2048)
        if not data:
            break
        response.extend(data)
    response = deserialize(response)
    # client_socket.shutdown(socket.SHUT_RD)
    return response

def sendReqToClient(request, clientIP, clientPort):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((clientIP, clientPort))
    client_socket.sendall(serialize(request))
    response = deserialize(client_socket.recv(2048))
    client_socket.shutdown(socket.SHUT_RDWR)
    return response

def modifyChunk(fileName,chunkID):
    #Can we do this?    
    pass

def rarestPeers(chunkInfo):
    #return map of chunk ID to (peerIP, peerPort)
    chunkToPeer = []
    chunkList = list(enumerate(chunkInfo))
    chunkList.sort(key = lambda x:len(x[1].peers) )
    for chunkId, chunk in chunkList:
        chunkToPeer.append((chunkId,chunk.peers[0]))
    
    return chunkToPeer

###########################
# Calls to server API
###########################

def registerNode(fileList):
    #Send register request to server - pass IP address, and file list
    #Get register status - success or failure
    peerIP = CLIENT_IP
    for fileName in fileList:
        fileMetadata = createFileMetadata(fileName)
        locFileMetadataMap[fileName] = fileMetadata
    request = Request(RegisterNode,(peerIP, locFileMetadataMap))
    response = sendReqToServer(request)
    print(f"Response: status - {response.Status}, body - {response.Body}")

def getFileList():
    #Send get file list request to server
    #Get list of file names
    #encode request
    #send on socket
    # rcv bytes and populate globalFileList
    request = Request(GetFileList, tuple())
    response = sendReqToServer(request)
    print(f"Response: status - {response.Status}, body - {response.Body}")
    global globFileList
    if response is not None:
        globFileList = response.Body
    #Overwriting the local list

def getFileMetadata(fileName):
    #Get the hosts and chunk info for each node where the file is present
    request = Request(GetFileMetadata, (fileName,))
    response = sendReqToServer(request)
    print(f"Response: status - {response.Status}, body - {response.Body}")
    global globFileMetadata
    if response is not None:
        globFileMetadata[fileName] = response.Body
        # FileMetadata.getObjFromResponse(response.Body['filename'],response.Body['size'],response.Body['chunkInfo'])

def registerChunk(fileName,chunkID):
    #Send filename and chunk ID
    #
    # send bytes on socket
    request = Request(RegisterChunk, (fileName, chunkID, CLIENT_IP))
    response = sendReqToServer(request)
    print(f"Response: status - {response.Status}, body - {response.Body}")

def downloadChunk(fileName,chunkID, srcIP, srcPort,file_data):
    #send
    downloadRequest = Request("DownloadChunk", (fileName, chunkID))
    response = sendReqToClient(downloadRequest, srcIP, srcPort)
    print(f"Download chunk Response: status - {response.status}, body - {response.body}")
    if response is not None:
        registerRequest = Request("RegisterChunk", (fileName, chunkID))
        registerResponse = sendReqToServer(registerRequest)
        print(f"Register chunk Response: status - {registerResponse.status}, body - {registerResponse.body}")
        file_data[chunkID] = response.Body

def downloadFile(fileName):
    #get list of chunks from server
    #TODO use multi-threading to download chunks parallely
    #once chunk is received, verify the chunk 
    getFileMetadata(fileName)
    fileMetadata = globFileMetadata[fileName]
    num_chunks = len(fileMetadata.chunkInfo)
    file_data = [None]*num_chunks
    chunkToPeer = rarestPeers(fileMetadata.chunkInfo)
    dloadThreads = []
    for chunkId, peer in chunkToPeer:
        peerIP, peerPort = peer
        dloadThreads.append(threading.Thread(target=downloadChunk, args=[fileName,chunkId,peerIP,peerPort,file_data]))
        print(f"Downloading chunk {chunkId} from {peer}")
        dloadThreads[-1].start()
        # file_data[chunkId] = downloadChunk(fileName, chunkId, peerIP, peerPort)
    print(f"Downloaded file {fileName}, contents: {file_data}")
    for t in dloadThreads:
        t.join()
    with open(FILES_DIR+"/"+fileName, 'wb') as f:
        f.write(b''.join(file_data))

##########################################
##############  UPLOAD PART  #############
##########################################
        
def uploadChunk(request):
    fileName,chunkID = request.Args
    with open(fileName, 'rb') as f:
        start = chunkID*CHUNK_SIZE
        f.seek(start)
        chunk = f.read(CHUNK_SIZE)
    return chunk

def socket_target(conn):
    serializedReq = bytearray()
    while True: 
        data = conn.recv(1024) 
        if not data: 
            break
        serializedReq.extend(data)
    serializedReq = bytes(serializedReq)
    request = deserialize(serializedReq)
    reqResponse = uploadChunk(request)
    serializedResp = serialize(reqResponse)
    conn.send(serializedResp)


def initClient():
    upload_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    upload_socket.bind((CLIENT_IP,CLIENT_PORT))
    upload_socket.listen(10) #Max 10 peers in the queue
    print("sdfsdfdsffdgdgdgdfg")
    while True:
        client_socket, addr = upload_socket.accept()
        print(f"Received download req from client: {client_socket}, {addr}")
        threading.Thread(target = socket_target, args = client_socket).start


if __name__ == "__main__":
    threading.Thread(target=initClient,args=[]).start()
    FILES_DIR = sys.argv[1]
    CLIENT_PORT = int(sys.argv[2])
    fileList = []
    for file in os.listdir(FILES_DIR):
        fileList.append(file)
    print(f"Files before request: {globFileList}")
    registerNode(fileList)
    getFileList()
    print(f"Files after rq: {globFileList}")
    print(f"File Metadata before: {globFileMetadata}")
    getFileMetadata('kdjfs')
    # print(f"File Metadata after: {len(locFileMetadataMap['abd'].chunkInfo)}")
    downloadFile('kdjfs')