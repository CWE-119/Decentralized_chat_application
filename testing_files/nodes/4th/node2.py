import socket
import sys
import threading

# Global variables
peers = set()
is_server = False
server_address = ('localhost', 10000)

def accept_connections(server_socket):
    global is_server
    while True:
        if is_server:
            # This node is acting as the server
            peer_socket, peer_address = server_socket.accept()
            peers.add(peer_socket)
            print(f'Connection established with {peer_address}')
        else:
            # Check if the main server is available
            try:
                with socket.create_connection(server_address, timeout=1):
                    pass
            except OSError:
                # The main server is down, so this node will act as the server
                is_server = True
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.bind(('localhost', 10000))
                server_socket.listen()
                print('This node is acting as the server.')

def handle_peer(peer_socket):
    global is_server
    while True:
        try:
            message = peer_socket.recv(1024)
            if message:
                print(f"received message: {message.decode()}")
            if is_server:
                # This node is acting as the server, so broadcast the message to all connected peers
                for peer in peers:
                    if peer != peer_socket:
                        peer.send(message)
            else:
                # Send the message to the main server
                with socket.create_connection(server_address, timeout=1) as server_socket:
                    server_socket.sendall(message)
        except ConnectionResetError:
            break
    peer_socket.close()
    peers.remove(peer_socket)
    print('Connection closed')

def broadcast_messages():
    global is_server
    while True:
        try:
            try:
                message = input("> ")
                if is_server:
                    # This node is acting as the server, so broadcast the message to all connected peers
                    for peer in peers:
                        peer.send(message.encode('utf-8'))
            except UnicodeDecodeError:
                print("Invalid input. Please enter valid input")
            else:
                # Send the message to the main server
                with socket.create_connection(server_address, timeout=1) as server_socket:
                    server_socket.sendall(message.encode())
        except KeyboardInterrupt:
            print("please close the program")

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 6969))
    server_socket.listen()

    # Start accepting connections on a separate thread
    accept_thread = threading.Thread(target=accept_connections, args=(server_socket,))
    accept_thread.start()

    # Start broadcasting messages on a separate thread
    broadcast_thread = threading.Thread(target=broadcast_messages)
    broadcast_thread.start()

if __name__ == '__main__':
    main()
