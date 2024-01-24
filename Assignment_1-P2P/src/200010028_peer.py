#preprocessor section
import socket
import time
import threading
import sys
import os

#global declarations

#address of this peer
address = ()
#directory containing the peer's shareable files
peerDirectory = sys.argv[1]
#peers in the network
peers = []
# the number of peers a peer can have is given as a command line argument
noOfConnections = 20
#buffer size
bufSize = 8192
#data structure that contains the merged file fragments
mergedFile = {}
dirPath = os.path.join(os.getcwd(),peerDirectory)
files = os.listdir(dirPath)
chunkTransfer = {}

#subprograms
def receiveMessage():
    while True:
        try:

            dataFromServer = clientSocket.recv(bufSize).decode("utf-8") 
            # print("Received list of peers from the Manager in the network.")
            if not dataFromServer:
                break
            else:
                updatePeers(dataFromServer) 
                    
        except KeyboardInterrupt:
            disconnect()


def updatePeers(data):
    global address,peers
    updatedPeers = data.split(':')[:-1]
    updatedPeers = [eval(p) for p in updatedPeers]
    if address in updatedPeers:
        updatedPeers.remove(address)
    peers = updatedPeers
    # print("The peers that I received: ",peers)
    

def fetchFile(num,start,peer,sendFileMessage):
    global mergedFile,chunkTransfer
    startOffset = str(counter) 
    numOfPeers = str(noOfPeers)
    sendFileMessage += " " + numOfPeers + " " + startOffset
    peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    peerSocket.connect(peer)
    peerSocket.sendall(sendFileMessage.encode("utf-8"))
    rcvData = peerSocket.recv(bufSize)
    # print("data: ",rcvData)
    if rcvData:
        mergedFile[start] = rcvData
        chunkTransfer[start] = True
    else:
        chunkTransfer[start] = False
    peerSocket.close()

def fileSharing(peerConnectionSocket,peerAddress):
    global files
    while True:
        try:
          
            receivedData = peerConnectionSocket.recv(bufSize).decode("utf-8")
            if receivedData and receivedData[0:2]=="f:":
                #peer requesting for file
                requestedFile = receivedData.split(':')[1]
                # print("Peer is requesting file: ",requestedFile)
                if requestedFile in files:
                    peerConnectionSocket.send("Yes".encode("utf-8"))
                else:
                    peerConnectionSocket.send("No".encode("utf-8"))
            elif receivedData and receivedData.split(" ")[0]=="send":

                receivedData = receivedData.split(" ")
                requestedFile = receivedData[1]
                num = int(receivedData[2])
                start = int(receivedData[3])

                if os.path.exists(os.path.join(dirPath,requestedFile)):
                    fileSize = os.path.getsize(os.path.join(dirPath,requestedFile))        
                    f = open(os.path.join(dirPath,requestedFile),'rb')
                    sendData = f.read()
                    cSize = len(sendData)
                    cSize = cSize//num
                    f.close()
                    data = sendData[start*cSize:start*cSize+cSize]
                    # print("Data I am sending: ",data)
                    peerConnectionSocket.sendall(data)
                    print("File sharing is done.")
                    print("Now, you can enter yes if you want to fetch a file and no if you want to disconnect.")

            peerConnectionSocket.close()
            break

        except KeyboardInterrupt:
            disconnect()
        
        except:
            continue

def shareFile():

    while True:
        try:
            peerConnectionSocket,peerAddress = serverSocket.accept()
            shareFileThread = threading.Thread(target=fileSharing,args=(peerConnectionSocket,peerAddress))
            shareFileThread.start()
            shareFileThread.join()
        except KeyboardInterrupt:
            disconnect()
        except:
            continue

       

def disconnect():
    print("Disconnected from the manager.")
    clientSocket.sendall("q".encode('utf-8'))
    clientSocket.close()
    serverSocket.close()  
    sys.exit() 

#main() function 
if __name__== '__main__':

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    clientSocket.connect(("localhost",8877))
    address = clientSocket.getsockname()
    # print("My address: ",address)

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind(address)
    serverSocket.listen(noOfConnections)

    messageThread = threading.Thread(target=receiveMessage)
    messageThread.daemon = True
    messageThread.start()

    shareThread = threading.Thread(target=shareFile)
    shareThread.daemon = True
    shareThread.start()


    while True:
        try: 
            choice = input("Please enter yes if you want to fetch a file and no if you want to disconnect from the server.")
            if choice=="yes":

                fileName = input("Please enter the file name that you want to fetch from your peers.")
                while True:
                    req = "f:"+ fileName
                    availablePeers = []
                    for p in peers:
                        peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        peerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        peerSocket.connect(p)
                        peerSocket.sendall(req.encode("utf-8"))
                        msg = peerSocket.recv(bufSize).decode("utf-8")
                        print(msg)
                        if msg and msg=="Yes":
                            print("Peer Ready to share file fragment.")
                            availablePeers.append(p)
                        peerSocket.close()

                    noOfPeers = len(availablePeers)
                        
                    if(noOfPeers==0):
                        print("Noone is available to share the file.Please try later.")
                        break
                    
                    fileThreads = []
                    sendFileMessage = "send " + fileName 
                    counter = 0
                    fileDir = os.path.join(dirPath, fileName)


                    #for receiving the file fragments in parallel
                    for peer in availablePeers:  
                        try:

                            fileThread = threading.Thread(target=fetchFile,args=(noOfPeers,counter,peer,sendFileMessage))
                            fileThreads.append(fileThread)
                            fileThread.start()
                            
                        except KeyboardInterrupt:
                            disconnect()
                        counter += 1
                        

                    for i in range(len(fileThreads)):
                        fileThreads[i].join()

                    # peersToRemove = []
                    # for chunk in chunkTransfer:
                    #     if not chunkTransfer[chunk]:
                    #         removePeer = availablePeers[chunk]
                    #         peersToRemove.append(removePeer)

                    # if len(peersToRemove)>0:
                    #     for p in peersToRemove:
                    #         availablePeers.remove(p)


                    #fragments are received by now

                    mergedFile = sorted(mergedFile.items())
            
                    if (len(mergedFile) == noOfPeers):
                        f = open(fileDir, "wb")
                        for startChunk in mergedFile:
                            f.write(startChunk[1])
                        f.close()
                        mergedFile = {}
                        print("I received the file: ",fileName)                         
                        break     

            elif choice=="no":
                disconnect()  
            else:
                print("You have to enter yes or no only.")
                continue      

        except KeyboardInterrupt:
                disconnect()
