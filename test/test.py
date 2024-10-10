import sys
import os
import shutil
sys.path.append('../src/')
from client import Client
from server import Server
from utils import *

def cleanup():
    try:
        os.path.exists("./test_1_1") and shutil.rmtree("./test_1_1")
        os.path.exists("./test_1_2") and shutil.rmtree("./test_1_2")
        os.path.exists("./test_2_1") and shutil.rmtree("./test_2_1")
        os.path.exists("./test_2_2") and shutil.rmtree("./test_2_2")
        os.path.exists("./test_3_1") and shutil.rmtree("./test_3_1")
        os.path.exists("./test_3_2") and shutil.rmtree("./test_3_2")
        os.path.exists("./test_3_3") and shutil.rmtree("./test_3_3")
    except:
        pass

def test1():
    logging.info("---------------------------------------------------------------------------------------------------------")
    logging.info("--- Standard test: 2 clients with upload/download --- ")
    logging.info("---------------------------------------------------------------------------------------------------------")
    try:
        os.mkdir("./test_1_1")
        shutil.copyfile("./files/abd", "./test_1_1/abd")
        shutil.copyfile("./files/bar", "./test_1_1/bar")
        os.mkdir("./test_1_2")
        shutil.copyfile("./files/img.jpg", "./test_1_2/img.jpg")
    except:
        pass
    server = Server()
    client1 =  Client("./test_1_1", 43210)
    logging.info(f"File list after client 1 register: {client1.getFileList()}")
    client2 = Client("./test_1_2", 44321)
    logging.info(f"File list after client 2 register: {client1.getFileList()}")
    client2.downloadFile("abd")
    client2.downloadFile("bar")
    client1.downloadFile("img.jpg")
    client1.stop()
    client2.stop()
    server.stop()

def test2():
    logging.info("---------------------------------------------------------------------------------------------------------")
    logging.info("--- Integrity test: 2 clients, modifying file should cause hash verification to fail --- ")
    logging.info("---------------------------------------------------------------------------------------------------------")
    try:
        os.mkdir("./test_2_1")
        shutil.copyfile("./files/foo", "./test_2_1/foo")
        os.mkdir("./test_2_2")
    except:
        pass
    server = Server()
    client1 =  Client("./test_2_1", 43210)
    logging.info(f"File list after client 1 register: {client1.getFileList()}")
    # replace foo with foo_modified
    os.remove("./test_2_1/foo")
    shutil.copyfile("./files/foo_modified", "./test_2_1/foo")
    client2 = Client("./test_2_2", 44321)
    logging.info(f"File list after client 2 register: {client1.getFileList()}")
    client2.downloadFile("foo")
    client1.stop()
    client2.stop()
    server.stop()

def test3():
    logging.info("---------------------------------------------------------------------------------------------------------")
    logging.info("--- Rarest first test: 3 clients, one with all chunks, one with partial chunks, one downloader ---")
    logging.info("--- 3rd client should download chunks based on rarity --- ")
    logging.info("---------------------------------------------------------------------------------------------------------")
    try:
        os.mkdir("./test_3_1")
        shutil.copyfile("./files/foo", "./test_3_1/foo")
        os.mkdir("./test_3_2")
        os.mkdir("./test_3_3")
    except:
        pass
    server = Server()
    client1 =  Client("./test_3_1", 43210)
    client2 = Client("./test_3_2", 54322)
    # Client 2 downloads foo with only half the chunks for testing
    client2.downloadFile("foo", omitChunk=True)
    client3 = Client("./test_3_3", 44322)
    client3.downloadFile("foo")
    client1.stop()
    client2.stop()
    client3.stop()
    server.stop()

cleanup()
test1()
test2()
test3()
