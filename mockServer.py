import socket
import threading
import time
import random

MAX_UNCHOKE = 4
REGULAR_UNCHOKE = 1
OPTIMISTICALLY_UNCHOKE = 3
class MockPeerServer:
    def __init__(self, host, port, pieces):
        self.host = host
        self.port = port
        self.pieces = pieces
        self.running = True
        self.connected = {}
        self.unchoke = []
        self.interested = {}

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"Peer server: started on {self.host}:{self.port}")
        while self.running:
            client_socket, addr = server.accept()
            self.connected[addr] = 0 # add connected peer to dict (key = (ip, port), value = downloadRate)
            thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
            thread.start()
        server.close()
        print("Peer server stopped.")

    def handle_client(self, client_socket, addr):
        # Get ip address and port number of client
        if (addr not in self.unchoke):
            client_socket.send(f'Choked')
            return
        request = client_socket.recv(1024).decode("utf-8")
        print(f"Peer server: Received request: {request}")
        if "REQUEST_PIECE" in request:
            _, piece_index = request.split("::")
            piece_index = int(piece_index)
            if piece_index < len(self.pieces):
                print(f"Peer server: Sending piece {piece_index}")
                client_socket.send(self.pieces[piece_index])
        client_socket.close()
    def stop(self):
        self.running = False
        # Tạo một kết nối giả để thoát khỏi accept() và dừng vòng lặp
        try:
            stop_socket = socket.create_connection((self.host, self.port))
            stop_socket.close()
        except Exception as e:
            print(f"Error stopping server: {e}")
    
    def updateDownloadRateForPeer(self, addr, rate):
        if addr in self.connected:
            self.connected[addr] = rate
        if addr in self.interested:
            self.interested[addr] = rate
    
    def resetDownloadRate(self):
        for key in self.connected:
            self.connected[key] = 0
        for key in self.interested:
            self.interested[key] = 0
        
    def reEvaluteTopPeers(self):
        while True:
            firstPriority = {}
            for key in self.interested:
                if key in self.connected:
                    firstPriority[key] = self.connected[key]
            lengthOfFirstPriority = len(firstPriority)
            if lengthOfFirstPriority == MAX_UNCHOKE:
                self.unchoke = firstPriority.keys()
            elif lengthOfFirstPriority < MAX_UNCHOKE:
                self.unchoke = firstPriority.keys()
                sortedConnected = sorted(self.connected.items(), key = lambda item: item[1], reverse = True)
                self.unchoke += [peer[0] for peer in sortedConnected[: MAX_UNCHOKE - lengthOfFirstPriority]]
            else:
                sortedFirstPriority = sorted(firstPriority.items(), key = lambda item : item[1], reverse = True)
                self.unchoke = [peer[0] for peer in sortedConnected[: MAX_UNCHOKE]]
            time.sleep(REGULAR_UNCHOKE)
            
    def optimisticallyUnchoke(self):
        while True:
            randomPeer = random.choice(self.connected.keys())
            if randomPeer in self.unchoke:
                continue
            else:
                self.unchoke.append(randomPeer)
            time.sleep(OPTIMISTICALLY_UNCHOKE)
    