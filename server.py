import socket
SERVER_PORT = 99999
SERVER_NAME = "localhost"

def registerNode(peerID,localFileList):
    #REturn register status - success or failure
    peerList.append(peerID)
    fileList.append(localFileList)

    return success

def getFileList():
    #REturn list of file names
    return fileList

def getFileMetadata(fileName):
    #REturn the hosts and chunk info for each node where the file is present
    return fileMetadataList[fileName]

def registerFile(fileMetaData, peerID):
    # recieves file meta datacalls registerChunk
    fileMetaDataList[fileName] = FileMetadata(fileMetaData.fileName, fileMetaData.size)
    for chunkInfo in fileMetaData.chunkInfo:
        registerChunk(fileMetaData.fileName,chunkInfo.chunkID, peerID)
    
def registerChunk(fileName,chunkID,peerID):
    #Return register status
    fileMetadataList[fileName].addPeer(chunkID,peerID)

def processRequest(request):
    #Get request type
    #Can be either:
        #Register request
        #Get file lists
        #Get file info
        #Chunk register request
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_NAME,SERVER_PORT))
    server_socket.listen(10)

    while True:
        client_socket, addr = server_socket.accept()

        req = server_socket.recv(4096) # send object here?? encoded???


peerList = [] # list of peers ??? needed???
fileList = [] # stores file list
fileMetadataList = []