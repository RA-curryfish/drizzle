import socket
from utils import *
import threading
import os
import random
import traceback


class Client:

    def __init__(self, files_dir, port):
        self.FILES_DIR = files_dir
        self.CLIENT_IP = socket.gethostbyname(socket.gethostname())
        self.CLIENT_PORT = port
        self.fileList = []
        for file in os.listdir(self.FILES_DIR):
            self.fileList.append(file)
        self.locFileMetadataMap = dict() # dict of fileName to fileMetadata
        self.globFileList = list() # list of all files in server
        self.globFileMetadata = dict() # dict of fileName to fileMetadata
        self.registerNode(self.fileList)
        threading.Thread(target=self.initUploadThread,args=[]).start()

    ############################
    #Local functionality
    ############################
    def getFilePath(self, fileName):
        return self.FILES_DIR+"/"+fileName

    def getFileSize(self, fileName):
        return os.path.getsize(self.getFilePath(fileName))

    def createFileMetadata(self, fileName):
        fileMetadata = FileMetadata(fileName, self.getFileSize(fileName), self.CLIENT_IP, self.CLIENT_PORT, self.getFilePath(fileName))
        return fileMetadata

    def sendReqToServer(self, request):
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

    def sendReqToClient(self, request, clientIP, clientPort):
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

    def rarestPeers(self, chunkInfo):
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

    def registerNode(self, fileList):
        #Send register request to server - pass IP address, and file list
        #Get register status - success or failure
        print("recvd register req")
        peerIP = self.CLIENT_IP
        for fileName in fileList:
            fileMetadata = self.createFileMetadata(fileName)
            self.locFileMetadataMap[fileName] = fileMetadata
        request = Request(RegisterNode,(peerIP, self.locFileMetadataMap))
        response = self.sendReqToServer(request)
        logging.debug(f"Response: status - {response.Status}, body - {response.Body}")

    def getFileList(self):
        #Send get file list request to server
        #Get list of file names
        #encode request
        #send on socket
        # rcv bytes and populate globalFileList
        request = Request(GetFileList, tuple())
        response = self.sendReqToServer(request)
        logging.debug(f"Response: status - {response.Status}, body - {response.Body}")
        if response is not None:
            self.globFileList = response.Body
        return self.globFileList
        #Overwriting the local list

    def getFileMetadata(self, fileName):
        #Get the hosts and chunk info for each node where the file is present
        request = Request(GetFileMetadata, (fileName,))
        response = self.sendReqToServer(request)
        logging.debug(f"Response: status - {response.Status}, body - {response.Body}")
        if response is not None:
            self.globFileMetadata[fileName] = response.Body
            # FileMetadata.getObjFromResponse(response.Body['filename'],response.Body['size'],response.Body['chunkInfo'])
        else:
            logging.error("File {fileName} not present in server")
            raise Exception()

    def registerChunk(self, fileName,chunkID, omitChunk):
        #Send filename and chunk ID
        # send bytes on socket
        if omitChunk and (chunkID%2 == 0):
            return Response(ReqStatus.SUCCESS, None)
        request = Request(RegisterChunk, (fileName, chunkID, self.CLIENT_IP, self.CLIENT_PORT))
        response = self.sendReqToServer(request)
        # logging.debug(f"Response: status - {response.Status}, body - {response.Body}")
        return response

    def downloadChunk(self, fileName,chunkID, srcIP, srcPort, hashValue, file_data, omitChunk):
        #send
        downloadRequest = Request("DownloadChunk", (fileName, chunkID))
        response = self.sendReqToClient(downloadRequest, srcIP, srcPort)
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
        registerResponse = self.registerChunk(fileName,chunkID, omitChunk)
        if registerResponse is not None:
            logging.debug(f"Register chunk Response: status - {registerResponse.Status}, body - {registerResponse.Body}")
            file_data[chunkID] = chunkData
            return
        else:
            logging.error("could not register chunk")

    def downloadFile(self, fileName, omitChunk=False):
        #get list of chunks from server
        #once chunk is received, verify the chunk 
        if fileName in self.locFileMetadataMap:
            logging.info(f"File {fileName} already exists on device")
            return
        try:
            self.getFileMetadata(fileName)
            fileMetadata = self.globFileMetadata[fileName]
            num_chunks = len(fileMetadata.chunkInfo)
            for chunkID, cinfo in enumerate(fileMetadata.chunkInfo):
                logging.info(f"Chunk {chunkID} present in {cinfo.peers}")
            file_data = [None]*num_chunks
            chunkToPeer = self.rarestPeers(fileMetadata.chunkInfo)
            dloadThreads = []
            for chunkId, peer in chunkToPeer:
                peerIP, peerPort = peer
                hashValue = fileMetadata.chunkInfo[chunkId].hashValue
                dloadThreads.append((
                    threading.Thread(target=self.downloadChunk, args=[fileName,chunkId,peerIP,peerPort,hashValue,file_data, omitChunk]),
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
            with open(self.getFilePath(fileName), 'wb') as f:
                f.write(b''.join(file_data))
            self.locFileMetadataMap[fileName] = fileMetadata
            logging.info(f"-- File {fileName} successfully downloaded -- ")
        except:
            logging.error(f"Error in downloading file: {fileName}")
            # if logging._Level == logging.DEBUG:
            #     traceback.print_exc()
            traceback.print_exc()

    ##########################################
    ##############  UPLOAD PART  #############
    ##########################################
            
    def uploadChunk(self, request):
        fileName,chunkID = request.Args
        with open(self.getFilePath(fileName), 'rb') as f:
            start = chunkID*CHUNK_SIZE
            f.seek(start)
            chunk = f.read(CHUNK_SIZE)
        return Response(ReqStatus.SUCCESS, chunk)

    def socket_target(self, conn):
        serializedReq = bytearray()
        while True: 
            data = conn.recv(1024) 
            if not data: 
                break
            serializedReq.extend(data)
        serializedReq = bytes(serializedReq)
        request = deserialize(serializedReq)
        logging.debug(f"REceived upload req")
        reqResponse = self.uploadChunk(request)
        serializedResp = serialize(reqResponse)
        conn.send(serializedResp)
        conn.shutdown(socket.SHUT_WR)

    def initUploadThread(self):
        upload_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        upload_socket.bind((self.CLIENT_IP,self.CLIENT_PORT))
        logging.info(f"Started peer, uploading on {(self.CLIENT_IP,self.CLIENT_PORT)}")
        upload_socket.listen(10) #Max 10 peers in the queue
        while True:
            client_socket, addr = upload_socket.accept()
            logging.debug(f"Received download req from client: {client_socket}, {addr}")
            threading.Thread(target = self.socket_target, args = [client_socket]).start()



# if __name__ == "__main__":

#     logging.debug(f"Files before request: {globFileList}")
#     registerNode(fileList)
#     getFileList()
#     logging.debug(f"Files after rq: {globFileList}")
#     # logging.debug(f"File Metadata before: {globFileMetadata}")
#     # getFileMetadata('xyz')
#     # logging.debug(f"File Metadata after: {len(locFileMetadataMap['abd'].chunkInfo)}")
#     if 'img.jpg' not in fileList:
#         downloadFile('img.jpg')
#         # getFileMetadata('abd')