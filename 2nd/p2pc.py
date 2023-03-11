# we are trying to achieve a P2P node , it is difficult to achieve with socket programming

# datagram protocol is for udp connections
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import random


def Client(DatagramProtocol):
    def __init__(self, host, port):
        if host == "localhost":
            host = "127.0.0.1"
        self.id = host, port
        self.address = None

    def datagramReceived(self, datagram, addr):
        print(addr, ":", datagram)

    # send message is responsible for our own messages
    def send_message(self):
        while True:
            self.transport.write(input("_>").encode("utf-8"), self.address)


if __name__ == '__main__':
    port = random.randint(1000, 5000)
    reactor.listenUDP(port, Client('localhost', port))
