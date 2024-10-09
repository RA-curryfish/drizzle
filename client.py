import socket
from utils import *
import threading
import os
import sys
import random
import traceback

CLIENT_IP = socket.gethostbyname(socket.gethostname())
CLIENT_PORT = None
FILES_DIR = ""

locFileMetadataMap = dict() # dict of fileName to fileMetadata
globFileList = list() # list of all files in server
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
    logging.debug(f"Connecting to server: {SERVER_NAME, SERVER_PORT}")
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
    logging.debug(f"Connecting to peer: {clientIP, clientPort}")
    client_socket.connect((clientIP, clientPort))
    client_socket.sendall(serialize(request))
    client_socket.shutdown(socket.SHUT_WR)
    response = bytearray()
    while True:
        data = client_socket.recv(2048)
        if not data:
            break
        response.extend(data)
    response = deserialize(response)
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
        chunkToPeer.append((chunkId,chunk.peers[random.randint(0,len(chunk.peers)-1)]))
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
    logging.debug(f"Response: status - {response.Status}, body - {response.Body}")

def getFileList():
    #Send get file list request to server
    #Get list of file names
    #encode request
    #send on socket
    # rcv bytes and populate globalFileList
    request = Request(GetFileList, tuple())
    response = sendReqToServer(request)
    logging.debug(f"Response: status - {response.Status}, body - {response.Body}")
    global globFileList
    if response is not None:
        globFileList = response.Body
    #Overwriting the local list

def getFileMetadata(fileName):
    #Get the hosts and chunk info for each node where the file is present
    request = Request(GetFileMetadata, (fileName,))
    response = sendReqToServer(request)
    logging.debug(f"Response: status - {response.Status}, body - {response.Body}")
    global globFileMetadata
    if response is not None:
        globFileMetadata[fileName] = response.Body
        # FileMetadata.getObjFromResponse(response.Body['filename'],response.Body['size'],response.Body['chunkInfo'])
    else:
        logging.error("File {fileName} not present in server")
        raise Exception()

def registerChunk(fileName,chunkID):
    #Send filename and chunk ID
    # send bytes on socket
    request = Request(RegisterChunk, (fileName, chunkID, CLIENT_IP, CLIENT_PORT))
    response = sendReqToServer(request)
    # logging.debug(f"Response: status - {response.Status}, body - {response.Body}")
    return response

def downloadChunk(fileName,chunkID, srcIP, srcPort, hashValue, file_data):
    #send
    downloadRequest = Request("DownloadChunk", (fileName, chunkID))
    response = sendReqToClient(downloadRequest, srcIP, srcPort)
    logging.debug(f"Download chunk Response: status - {response.Status}, body - {response.Body}")
    if response is None:
        logging.error(f"Download chunk Response: status - {response.Status}, body - {response.Body}")
        # raise Exception("Could not download chunk {chunkID} for file {fileName}")
        return
    chunkData = response.Body
    #Verify chunk
    if getHash(chunkData) != hashValue:
        logging.error(f"Hash mismatch for chunk {chunkID} of file {fileName}")
        # raise Exception()
        return
    registerResponse = registerChunk(fileName,chunkID)
    if registerResponse is not None:
        logging.debug(f"Register chunk Response: status - {registerResponse.Status}, body - {registerResponse.Body}")
        file_data[chunkID] = chunkData
        return
    else:
        logging.error("could not register chunk")

def downloadFile(fileName):
    #get list of chunks from server
    #once chunk is received, verify the chunk 
    if fileName in locFileMetadataMap:
        logging.info(f"File {fileName} already exists on device")
        return
    try:
        getFileMetadata(fileName)
        fileMetadata = globFileMetadata[fileName]
        num_chunks = len(fileMetadata.chunkInfo)
        for chunkID, cinfo in enumerate(fileMetadata.chunkInfo):
            logging.info(f"Chunk {chunkID} present in {cinfo.peers}")
        file_data = [None]*num_chunks
        chunkToPeer = rarestPeers(fileMetadata.chunkInfo)
        dloadThreads = []
        for chunkId, peer in chunkToPeer:
            peerIP, peerPort = peer
            hashValue = fileMetadata.chunkInfo[chunkId].hashValue
            dloadThreads.append((
                threading.Thread(target=downloadChunk, args=[fileName,chunkId,peerIP,peerPort,hashValue,file_data]),
                chunkId))
            logging.info(f"Downloading chunk {chunkId} from {peer}")
            dloadThreads[-1][0].start()
            # file_data[chunkId] = downloadChunk(fileName, chunkId, peerIP, peerPort)
        for i, thr in enumerate(dloadThreads):
            t, cID = thr
            t.join()
            if file_data[cID] is None:
                raise Exception(f"Could not download chunk {cID}")
            printProgressBar(i+1,num_chunks,fileName)
        logging.debug(f"Downloaded file {fileName}, contents: {file_data}")
        with open(getFilePath(fileName), 'wb') as f:
            f.write(b''.join(file_data))
        locFileMetadataMap[fileName] = fileMetadata
    except:
        logging.error(f"Error in downloading file: {fileName}")
        # if logging._Level == logging.DEBUG:
        #     traceback.print_exc()
        traceback.print_exc()

##########################################
##############  UPLOAD PART  #############
##########################################
        
def uploadChunk(request):
    fileName,chunkID = request.Args
    with open(getFilePath(fileName), 'rb') as f:
        start = chunkID*CHUNK_SIZE
        f.seek(start)
        chunk = f.read(CHUNK_SIZE)
    return Response(ReqStatus.SUCCESS, chunk)

def socket_target(conn):
    serializedReq = bytearray()
    while True: 
        data = conn.recv(1024) 
        if not data: 
            break
        serializedReq.extend(data)
    serializedReq = bytes(serializedReq)
    request = deserialize(serializedReq)
    logging.debug(f"REceived upload req")
    reqResponse = uploadChunk(request)
    serializedResp = serialize(reqResponse)
    conn.send(serializedResp)
    conn.shutdown(socket.SHUT_WR)


def initClient():
    upload_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    upload_socket.bind((CLIENT_IP,CLIENT_PORT))
    logging.info(f"Started peer, uploading on {(CLIENT_IP,CLIENT_PORT)}")
    upload_socket.listen(10) #Max 10 peers in the queue
    while True:
        client_socket, addr = upload_socket.accept()
        logging.debug(f"Received download req from client: {client_socket}, {addr}")
        threading.Thread(target = socket_target, args = [client_socket]).start()


if __name__ == "__main__":
    threading.Thread(target=initClient,args=[]).start()
    FILES_DIR = sys.argv[1]
    CLIENT_PORT = int(sys.argv[2])
    fileList = []
    for file in os.listdir(FILES_DIR):
        fileList.append(file)
    logging.debug(f"Files before request: {globFileList}")
    registerNode(fileList)
    getFileList()
    logging.debug(f"Files after rq: {globFileList}")
    # logging.debug(f"File Metadata before: {globFileMetadata}")
    # getFileMetadata('xyz')
    # logging.debug(f"File Metadata after: {len(locFileMetadataMap['abd'].chunkInfo)}")
    if 'abd' not in fileList:
        downloadFile('abd')
        getFileMetadata('abd')