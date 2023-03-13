import socket
import thread
def handleSetServer(self):
    if self.serverSoc != None:
        self.serverSoc.close()
        self.serverSoc = None
        self.serverStatus = 0
    serveraddr = (self.serverIPVar.get().replace(' ', ''), int(self.serverPortVar.get().replace(' ', '')))
    try:
        self.serverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSoc.bind(serveraddr)
        self.serverSoc.listen(5)
        self.setStatus("Server listening on %s:%s" % serveraddr)
        thread.start_new_thread(self.listenClients, ())
        self.serverStatus = 1
        self.name = self.nameVar.get().replace(' ', '')
        if self.name == '':
            self.name = "%s:%s" % serveraddr
    except:
        self.setStatus("Error setting up server")


def listenClients(self):
    while 1:
        clientsoc, clientaddr = self.serverSoc.accept()
        self.setStatus("Client connected from %s:%s" % clientaddr)
        self.addClient(clientsoc, clientaddr)
        thread.start_new_thread(self.handleClientMessages, (clientsoc, clientaddr))
    self.serverSoc.close()


def handleAddClient(self):
    if self.serverStatus == 0:
        self.setStatus("Set server address first")
        return
    clientaddr = (self.clientIPVar.get().replace(' ', ''), int(self.clientPortVar.get().replace(' ', '')))
    try:
        clientsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsoc.connect(clientaddr)
        self.setStatus("Connected to client on %s:%s" % clientaddr)
        self.addClient(clientsoc, clientaddr)
        thread.start_new_thread(self.handleClientMessages, (clientsoc, clientaddr))
    except:
        self.setStatus("Error connecting to client")


def handleClientMessages(self, clientsoc, clientaddr):
    while 1:
        try:
            data = clientsoc.recv(self.buffsize)
            if not data:
                break
            self.addChat("%s:%s" % clientaddr, data)
        except:
            break
    self.removeClient(clientsoc, clientaddr)
    clientsoc.close()
    self.setStatus("Client disconnected from %s:%s" % clientaddr)


def handleSendChat(self):
    if self.serverStatus == 0:
        self.setStatus("Set server address first")
        return
    msg = self.chatVar.get().replace(' ', '')
    if msg == '':
        return
    self.addChat("me", msg)
    for client in self.allClients.keys():
        client.send(msg)


def addChat(self, client, msg):
    self.receivedChats.config()
    self.receivedChats.insert("end", client + ": " + msg + "\n")
    self.receivedChats.config(state=None)


def addClient(self, clientsoc, clientaddr):
    self.allClients[clientsoc] = self.counter
    self.counter += 1
    self.friends.insert(self.counter, "%s:%s" % clientaddr)


def removeClient(self, clientsoc, clientaddr):
    print(self.allClients)
    self.friends.delete(self.allClients[clientsoc])
    del self.allClients[clientsoc]
    print(self.allClients)


def setStatus(self, msg):
    self.statusLabel.config(text=msg)
    print(msg)
