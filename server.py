def registerNode(peerID,fileList):
    #REturn register status - success or failure
    peerList.append(peerID)
    fileList.append(fileList)
    return success
    pass

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
    pass

peerList = [] # list of peers ??? needed???
fileList = [] # stores file list
fileMetadataList = []