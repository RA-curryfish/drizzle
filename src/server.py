import socket
import threading
from utils import *

class Server:
    # Initilizer constructor of the server. Sets up empty lists and maps
    def __init__(self):
        self.stopServer = False
        self.serverThread = threading.Thread(target = self.initServer, args = [])
        self.serverThread.start()
        self.peerList = set() # list of peers ??? needed???
        self.fileList = set() # stores file list
        self.fileMetadataMap = dict() #Filename(str) to FileMetadata object

    # Stops the server by shutting down sockets and waiting for threads to wrap up.
    def stop(self):
        self.stopServer = True
        self.server_socket.shutdown(socket.SHUT_RDWR)
        self.serverThread.join()

    # Handles registering of client by appending to list of peers and updating the file metadata map with whatever the client wants to share. Returns status of operation
    def registerNode(self, peerID,clientfileMetadataMap):
        self.peerList.add(peerID)
        self.fileList.update(clientfileMetadataMap.keys())
        self.fileMetadataMap.update(clientfileMetadataMap)
        out = Response(ReqStatus.SUCCESS,None)
        return out

    # Returns a list of files that exist in the p2p system to the requesting client.
    def getFileList(self):
        out = Response(ReqStatus.SUCCESS,self.fileList)
        return out

    # Returns file metadata for a particular file to the requesting client. The metadata map is indexed into using the filename.
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
    
    # Updates the peer information who just successfully downloaded this particular chunk of the file, so that newer peers may download from here as well. Returns status of operation
    def registerChunk(self, fileName,chunkID,peerIP, peerPort):
        #Return register status
        self.fileMetadataMap[fileName].addPeer(chunkID,peerIP,peerPort)
        return Response(ReqStatus.SUCCESS,None)

    # Helper function that maps the request type to the correct API. Returns the result of the operation
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

    # Target function of the thread that handles requests by calling process request function
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

    # Initializes the server by binding on port and listens to requests.
    def initServer(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((SERVER_NAME,SERVER_PORT))
        self.server_socket.listen(10) #Max 10 peers in the queue
        logging.info(f"Server started on {SERVER_NAME}:{SERVER_PORT}")
        ## TESTING ONLY
        # socket_target(None)
        ## TESTING END
        while not self.stopServer:
            try:
                client_socket, addr = self.server_socket.accept()
                logging.debug(f"Received req from client: {addr}")
                threading.Thread(target = self.socket_target, args = [client_socket]).start()
            except:
                break
        logging.info("Server shutting down")

