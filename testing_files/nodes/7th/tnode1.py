import socket
import threading
from queue import Queue
import sys
# set the host and port of this node
HOST = '127.0.0.1'
PORT = 6969

# set the IP address and port of a known node in the network
KNOWN_HOST = '127.0.0.1'
KNOWN_PORT = 6969

# create a server socket to listen for incoming connections
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

# create a client socket to connect to the known node
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((KNOWN_HOST, KNOWN_PORT))

# create a thread-safe queue to store messages to be broadcasted
message_queue = Queue()


# function to handle incoming connections from other nodes
def handle_peer(peer_socket, peer_address):
    while True:
        try:
            message = peer_socket.recv(1024)
            if not message:
                # the connection was closed by the peer
                print(f'{peer_address} disconnected')
                break
            print(f'Received message from {peer_address}: {message.decode()}')
            # add the message to the queue to be broadcasted
            message_queue.put((message, peer_socket))
        except ConnectionResetError:
            pass
        except OSError:
            sys.exit()

# function to connect to a new peer
def connect_to_peer(peer_host, peer_port):
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        peer_socket.connect((peer_host, peer_port))
        threading.Thread(target=handle_peer, args=(peer_socket, (peer_host, peer_port))).start()
        print(f'Connected to peer at {peer_host}:{peer_port}')
        return peer_socket
    except:
        print(f'Failed to connect to peer at {peer_host}:{peer_port}')
        return None


# list to store the sockets of all connected nodes
connected_peers = []

# join the network by connecting to the known node
known_peer_socket = connect_to_peer(KNOWN_HOST, KNOWN_PORT)
if known_peer_socket:
    connected_peers.append(known_peer_socket)


# start listening for incoming connections
def accept_connections():
    while True:
        try:
            peer_socket, peer_address = server_socket.accept()
            threading.Thread(target=handle_peer, args=(peer_socket, peer_address)).start()
            print(f'Accepted connection from {peer_address}')
            connected_peers.append(peer_socket)
        except OSError:
            sys.exit()


threading.Thread(target=accept_connections).start()


# thread function to broadcast messages
def broadcast_messages():
    while True:
        message, sender_socket = message_queue.get()
        for peer_socket in connected_peers:
            if peer_socket != sender_socket:
                peer_socket.send(message.encode())


# start the thread to broadcast messages
threading.Thread(target=broadcast_messages).start()

# send messages to other nodes
while True:
    try:
        message = input('> ')
        message = message.encode()
        client_socket.send(message)

        # connect to a new peer if the user enters an IP address and port
        if ':' in message.decode():
            peer_host, peer_port = message.decode().split(':')
            peer_socket = connect_to_peer(peer_host, int(peer_port))
            if peer_socket:
                connected_peers.append(peer_socket)

        # add the message to the queue to be broadcasted
        message_queue.put((message, client_socket))

    except KeyboardInterrupt:
        break

# close all sockets
for peer_socket in connected_peers:
    peer_socket.close()
server_socket.close()
client_socket.close()
