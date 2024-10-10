import socket
import threading
from utils import *

class Server:
    def __init__(self):
        threading.Thread(target = self.initServer, args = []).start()
        self.peerList = set() # list of peers ??? needed???
        self.fileList = set() # stores file list
        self.fileMetadataMap = dict() #Filename(str) to FileMetadata object

    def registerNode(self, peerID,clientfileMetadataMap):
        self.peerList.add(peerID)
        self.fileList.update(clientfileMetadataMap.keys())
        self.fileMetadataMap.update(clientfileMetadataMap)
        out = Response(ReqStatus.SUCCESS,None)
        return out

    def getFileList(self):
        out = Response(ReqStatus.SUCCESS,self.fileList)
        return out

    def getFileMetadata(self, fileName):
        logging.debug(self.fileMetadataMap[fileName])
        out = Response(ReqStatus.SUCCESS,self.fileMetadataMap[fileName])
        return out

    # def registerFile(fileMetaData, peerID):
    #     global fileMetadataMap
    #     fileMetadataMap[fileMetaData.fileName] = FileMetadata(fileMetaData.fileName, fileMetaData.size)
    #     for chunkInfo in fileMetaData.chunkInfo:
    #         registerChunk(fileMetaData.fileName,chunkInfo.chunkID, peerID)
    #     return Response(ReqStatus.SUCCESS,None)
        
    def registerChunk(self, fileName,chunkID,peerIP, peerPort):
        #Return register status
        self.fileMetadataMap[fileName].addPeer(chunkID,peerIP,peerPort)
        return Response(ReqStatus.SUCCESS,None)

    def processRequest(self, request):
        #Can be either:Register request, Get file lists, Get file info, Chunk register request
        out = None
        logging.debug(f"Request: {request.RequestType}")
        if (request.RequestType == RegisterNode):
            peerIP = request.Args[0]
            clientFileMetaDataMap = request.Args[1]
            assert( (peerIP is not None) and (clientFileMetaDataMap is not None))
            out = self.registerNode(peerIP,clientFileMetaDataMap)
        elif (request.RequestType == GetFileList):
            out = self.getFileList()
        elif (request.RequestType == GetFileMetadata):
            fileName = request.Args[0]
            assert(fileName is not None)
            out = self.getFileMetadata(fileName)
        elif (request.RequestType == RegisterChunk):
            fileName = request.Args[0]
            chunkID = request.Args[1]
            peerIP = request.Args[2]
            peerPort = request.Args[3]
            out = self.registerChunk(fileName, chunkID, peerIP, peerPort)
        return out

    def socket_target(self, conn):
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
        #     logging.debug(peerList[0])
        #     logging.debug(fileList[0])
        #     logging.debug(fileMetadataMap[filename].size)
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
        reqResponse = self.processRequest(request)
        serializedResp = serialize(reqResponse)
        conn.send(serializedResp)
        conn.shutdown(socket.SHUT_WR)

    def initServer(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((SERVER_NAME,SERVER_PORT))
        server_socket.listen(10) #Max 10 peers in the queue
        logging.info(f"Server started on {SERVER_NAME}:{SERVER_PORT}")
        ## TESTING ONLY
        # socket_target(None)
        ## TESTING END
        while True:
            client_socket, addr = server_socket.accept()
            logging.debug(f"Received req from client: {addr}")
            threading.Thread(target = self.socket_target, args = [client_socket]).start()
        logging.debug("does not reach")

