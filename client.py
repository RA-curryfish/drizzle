def registerNode():
    #Send register request to server - pass IP address, and metadata for all the files you have
    #Get register status - success or failure
    pass

def getFileList():
    #Send get file list request to server
    #Get list of file names
    pass

def getFileMetadata():
    #Get the hosts and chunk info for each node where the file is present
    pass

def registerChunk():
    #Send filename and chunk ID
    pass

def downloadChunk():
    #send
    pass

def downloadFile():
    #get list of chunks from server
    #use rarest first to determine order of chunks
    #use multi-threading to download chunks parallely
    #once chunk is received, verify the chunk 
    pass
