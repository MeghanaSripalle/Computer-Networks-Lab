#preprocessor section
import socket
import os
import sys
import threading
import time

#global declarations
managerHost = 'localhost'
managerPort = 8877
noOfConnections = 20 # the number of peers a manager can have 
bufSize = 8192  #buffer size 
connections = [] #list of peers' connection sockets
peers = []
connectionAddress = {}

#subprograms
def checkPeers(host,port):
    address = (host,port)
    try:      
        while True:         
            peerData = connectionAddress[address].recv(bufSize).decode('utf-8')
            if peerData and peerData == 'q':
                disconnect(connectionAddress[address],address)
                break
    
    except KeyboardInterrupt as e:
            sys.exit()


def run():
    
    try:
        managerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        managerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        managerSocket.bind((managerHost,managerPort))
        managerSocket.listen(noOfConnections)
        print("Manager is now running on port " + str(managerPort)) 
        
        while True:
            peer, address = managerSocket.accept()
            peers.append(address)
            connections.append(peer)
            connectionAddress[address] = peer
            print("The current active peers are: {}".format(peers) )
            broadcast()         
            print("{} has been added to the network.".format(address))
            managerThread = threading.Thread(target=checkPeers, args=(address))
            managerThread.daemon = True
            managerThread.start() 
            

    except KeyboardInterrupt as e:
        managerSocket.close()
        sys.exit()

def disconnect(con,add):
    try:
        connections.remove(con)
        peers.remove(add)
        del connectionAddress[add]
        con.close()
        broadcast()
        print("{}, disconnected from the network".format(add))
    except KeyboardInterrupt as e:
        sys.exit()

def broadcast():
    try:
        sendPeersData = ""
        for p in peers:
            sendPeersData += str(p) + ":"
        data = bytes(sendPeersData, 'utf-8')
        for conn in connections:
            conn.sendall(data)
    except KeyboardInterrupt as e:
        sys.exit()
     
#main() function           
if __name__ == '__main__':
    run()