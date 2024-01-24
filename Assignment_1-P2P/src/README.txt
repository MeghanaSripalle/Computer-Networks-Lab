CODE FILES:

200010028_manager.py: This file is responsible for running the manager in the network.
    > run(): the function responsible for the execution of the manager code.
        1. A manager socket is created and binds to a host and port to listen to the peers.
        2. The manager adds the new peer to the list of peers and broadcasts the list of peers to the other peers.
        3. Every time a peer connects, a thread is created for the peer to communicate with the peer 
    > checkPeers(): the function responsible for always transmitting the updated list of peers to the peer
        1. If the peer communicates that it wants to disconnect, then this function calls disconnect()
    > disconnect(): the function responsible for removing a peer when it communicates that it wants to leave the network
    > broadcast(): the function responsible for broadcasting the list of active peers to rest of the peers in the network

200010028_peer.py: This file is responsible for running the peer in the network
    > The command line arguments: the peer directory name (should be in current directory)
    > files refers to the list of shareable files
    > main(): the function responsible for running the peer.
        1. A socket is created for listening to the manager. Then a socket is created for listening to the peers.
        2. A file can be requested or the peer can choose to disconnect.
        3. When a file is requested, the file name has to be given as input. 
        4. Using the received peers list, the peer connects to those peers and asks them if they have the file. If they have the file, they are added to the available peers list.
        5. Now, the peer connects to those available peers to get the respective fragments of the file.
        6. After receiving the fragments, they are merged accordingly and written in the directory.
    > receiveMessage(): the function responsible for receiving the data from the manager (the updated list of peers).[pinging the manager and getting the list of peers]
        1. Whenever it receives data from the manager, it updates its own peers list. by calling updatePeers() on the received data.
    > updatePeers(): the function resposible for updating the peers list
    > fetchFile(): the function responsible for fetching the file fragment from the peer given in the arguments
        1. The peer connects to the given peer using a TCP socket to send the 'sendFileMessage' which contains information regarding the file and fragment to be sent.
        2. The peer fetches the fragment and stores it in a data structure called mergedFile.
    > shareFile(): the function responsible for sharing a file when requested by other peers.
        1. Whenever a peer requests this peer, a thread is created which runs on the fileSharing() function.
        2. We have the wait for this thread to finish to execute another thread(peer) by using thread.join().
    > fileSharing(): the function which the threads execute for actual file sharing.
        1. The data received from the peer is analysed.
        2. If the peer is asking if this peer has a particular file, this peer checks if the file is in its allocated directory.
        3. It sends 'Yes' if it is there and 'No' if it does not have the file.
        4. If the peer is asking this peer to send a fragment from the file. This peer sends that particular fragment.
    > disconnect(): the function responsible for disconnecting from the network
        1. When the peer wants to disconnect, a 'q' is sent to the manager and the sockets are closed.

PROGRAM STRUCTURE:
The program elements have been denoted for both the files in the comments of the files.

DEMO INSTRUCTIONS:
1. To run the manager: python3 200010028_manager.py 
2. To run the peer: python3 200010028_peer.py <peer_directory>
3. <peer_directory> refers to the directory in which the peer's shareable files will be stored.
4. When you run the peer file, you are asked to enter 'yes' if you want to fetch a file from your peers and 'no' if you wish to disconnect.
5. If you enter 'yes', then you will be asked to enter the name of the file that you wish to fetch.
6. If noone can share the file, then you are asked again.
7. The merged file is written in your directory.
8. If you enter 'no', you disconnect from the network.

THE LINK TO THE DEMO:
https://drive.google.com/file/d/1KB9XfcNSGqKzZNUxQOtNFLLNnndL3Amn/view?usp=sharing

