import socket
from data_structures import *
import threading
import os

SERVER_PORT = 9999
SERVER_NAME = "localhost"
CLIENT_IP = "localhost"
CLIENT_PORT = 4321

locFileMetadataMap = dict() # dict of fileName to fileMetadata
globFileList = list() 
globFileMetadata = dict() # dict of fileName to fileMetadata

############################
#Local functionality
############################
def getFileSize(fileName):
    # TODO implement
    return 0

def getFile(fileName):
    #TODO implement
    pass

def createFileMetadata(fileName):
    fileMetadata = FileMetadata(fileName, getFileSize(fileName), CLIENT_IP, CLIENT_PORT, getFile(fileName))
    return fileMetadata

def sendReqToServer(request):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_NAME,SERVER_PORT))
    client_socket.sendall(serialize(request))
    response = deserialize(client_socket.recv(2048))
    client_socket.shutdown(socket.SHUT_RDWR)
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
    chunkToPeer = dict()
    for chunkId, chunk in enumerate(chunkInfo):
        chunkToPeer[chunkId] = chunkInfo.peers[0]
    return chunkToPeer

###########################
# Calls to server API
###########################

def registerNode(fileList):
    #Send register request to server - pass IP address, and file list
    #Get register status - success or failure
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerIP = CLIENT_IP #TODO client own IP, check
    client_socket.connect((SERVER_NAME,SERVER_PORT))
    for fileName in fileList:
        fileMetadata = createFileMetadata(fileName)
        locFileMetadataMap[fileName] = fileMetadata
    request = Request(RegisterNode,(peerIP, locFileMetadataMap))
    client_socket.sendall(serialize(request))
    client_socket.shutdown(socket.SHUT_WR)
    response = deserialize(client_socket.recv(2048))
    print(f"Response: status - {response.Status}, body - {response.Body}")
    client_socket.shutdown(socket.SHUT_RDWR)

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
        globFileList = response
    #Overwriting the local list

def getFileMetadata(fileName):
    #Get the hosts and chunk info for each node where the file is present
    request = Request(GetFileMetadata, (fileName,))
    response = sendReqToServer(request)
    print(f"Response: status - {response.Status}, body - {response.Body}")
    global globFileMetadata
    if response is not None:
        globFileMetadata[fileName] = response

def registerChunk(fileName,chunkID):
    #Send filename and chunk ID
    #
    # send bytes on socket
    request = Request(RegisterChunk, (fileName, chunkID, CLIENT_IP))
    response = sendReqToServer(request)
    print(f"Response: status - {response.Status}, body - {response.Body}")

def downloadChunk(fileName,chunkID, srcIP, srcPort):
    #send
    downloadRequest = Request("DownloadChunk", (fileName, chunkID))
    response = sendReqToClient(downloadRequest, srcIP, srcPort)
    print(f"Download chunk Response: status - {response.status}, body - {response.body}")
    if response is not None:
        registerRequest = Request("RegisterChunk", (fileName, chunkID))
        registerResponse = sendReqToServer(registerRequest)
        print(f"Register chunk Response: status - {registerResponse.status}, body - {registerResponse.body}")

def downloadFile(fileName):
    #get list of chunks from server
    #TODO use rarest first to determine order of chunks
    #TODO use multi-threading to download chunks parallely
    #once chunk is received, verify the chunk 
    getFileMetadata(fileName)
    fileMetadata = globFileMetadata[fileName]
    num_chunks = len(fileMetadata.chunkInfo)
    file_data = [None]*num_chunks
    chunkToPeer = rarestPeers(fileMetadata.chunkInfo)
    for chunkId, peer in chunkToPeer.items():
        peerIP, peerPort = peer
        file_data[chunkId] = downloadChunk(fileName, chunkId, peerIP, peerPort)    
    print(f"Downloaded file {fileName}, contents: {file_data}")
    with open(fileName, 'wb') as f:
        f.write(''.join(file_data))

##########################################
##############  UPLOAD PART  #############
##########################################
        
def uploadChunk(request):
    #send
    fileName,chunkID = request.Args
    #TODO read chunk from file and send
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
    while True:
        client_socket, addr = upload_socket.accept()
        print(f"Received download req from client: {client_socket}, {addr}")
        threading.Thread(target = socket_target, args = client_socket).start


if __name__ == "__main__":
    threading.Thread(target=initClient,args=None).start
    # initClient()
    fileList = []
    for file in os.listdir("files"):
        fileList.append(file)
    print(fileList)
    registerNode(fileList)