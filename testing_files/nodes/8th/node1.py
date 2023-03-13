import socket
import threading

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


# function to handle incoming connections from other nodes
def handle_peer(peer_socket, peer_address):
    while True:
        message = peer_socket.recv(1024)
        if not message:
            # the connection was closed by the peer
            print(f'{peer_address} disconnected')
            break
        print(f'Received message from {peer_address}: {message.decode()}')


# function to connect to a new peer
def connect_to_peer(peer_host, peer_port):
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        peer_socket.connect((peer_host, peer_port))
        threading.Thread(target=handle_peer, args=(peer_socket, (peer_host, peer_port))).start()
        print(f'Connected to peer at {peer_host}:{peer_port}')
        return True
    except:
        print(f'Failed to connect to peer at {peer_host}:{peer_port}')
        return False


# join the network by connecting to the known node
connect_to_peer(KNOWN_HOST, KNOWN_PORT)


# start listening for incoming connections
def accept_connections():
    while True:
        peer_socket, peer_address = server_socket.accept()
        threading.Thread(target=handle_peer, args=(peer_socket, peer_address)).start()
        print(f'Accepted connection from {peer_address}')


threading.Thread(target=accept_connections).start()

# send messages to other nodes
while True:
    try:
        message = input('> ')
        client_socket.send(message.encode())

        # connect to a new peer if the user enters an IP address and port
        if ':' in message:
            peer_host, peer_port = message.split(':')
            connect_to_peer(peer_host, int(peer_port))
    except KeyboardInterrupt:
        pass