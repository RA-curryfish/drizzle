import sys
import os
import shutil
sys.path.append('../src/')
from client import Client
from server import Server
from utils import *

def test1():
    try:
        os.mkdir("./files_1")
        shutil.copyfile("./files/abd", "./files_1/abd")
        os.mkdir("./files_2")
        shutil.copyfile("./files/img.jpg", "./files_2/img.jpg")
    except:
        pass
    server = Server()
    client1 =  Client("./files_1", 43210)
    print(client1.getFileList())
    client2 = Client("./files_2", 44321)
    print(client1.getFileList())
    client2.downloadFile("abd")
    client1.downloadFile("img.jpg")

test1()