import socket
import json
from data_structures import *

SERVER_PORT = 99999
SERVER_NAME = "localhost"
CLIENT_IP = "localhost"

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

def createFileMetadata(fileName, peerIP):
    fileMetadata = FileMetadata(fileName, getFileSize(fileName), peerIP, getFile(fileName))
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
    for fileName in fileList:
        fileMetadata = createFileMetadata(fileName, peerIP)
        locFileMetadataMap[fileName] = fileMetadata
    request = Request("RegisterNode",(peerIP, locFileMetadataMap))
    client_socket.sendall(serialize(request))
    response = deserialize(client_socket.recv(2048))
    print(f"Response: status - {response.status}, body - {response.body}")
    client_socket.shutdown(socket.SHUT_RDWR)

def getFileList():
    #Send get file list request to server
    #Get list of file names
    #encode request
    #send on socket
    # rcv bytes and populate globalFileList
    request = Request("GetFileList", tuple())
    response = sendReqToServer(request)
    print(f"Response: status - {response.status}, body - {response.body}")
    global globFileList
    if response is not None:
        globFileList = response
    #Overwriting the local list

def getFileMetadata(fileName):
    #Get the hosts and chunk info for each node where the file is present
    request = Request("GetFileMetadata", (fileName,))
    response = sendReqToServer(request)
    print(f"Response: status - {response.status}, body - {response.body}")
    global globFileMetadata
    if response is not None:
        globFileMetadata[fileName] = response

def registerChunk(fileName,chunkID):
    #Send filename and chunk ID
    #
    # send bytes on socket
    request = Request("RegisterChunk", (fileName, chunkID, CLIENT_IP))
    response = sendReqToServer(request)
    print(f"Response: status - {response.status}, body - {response.body}")

def downloadChunk(fileName,chunkID, srcIP, srcPort):
    #send
    downloadRequest = Request("DownloadChunk", (fileName, chunkID))
    response = sendReqToClient(downloadRequest, srcIP, srcPort)
    print(f"Download chunk Response: status - {response.status}, body - {response.body}")
    if response is not None:
        registerRequest = Request("RegisterChunk", (fileName, chunkID))
        registerResponse = sendReqToServer(registerRequest)
        print(f"Register chunk Response: status - {registerResponse.status}, body - {registerResponse.body}")

def downloadFile():
    #get list of chunks from server
    #use rarest first to determine order of chunks
    #use multi-threading to download chunks parallely
    #once chunk is received, verify the chunk 
    pass

def uploadChunk(fileName,chunkID):
    #send
    
    pass



#Local functionality
