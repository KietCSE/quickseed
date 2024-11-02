import threading
import random
import socket

MAX_REGULAR_UNCHOKE = 4
REGULAR_UNCHOKE = 10
OPTIMISTICALLY_UNCHOKE = 30
MAX_CONNECTION = 15

class P2PUploader:
    def __init__(self, host, port, pieces, interested: dict = {}, unchoke: list = [], connected: dict = {}):
        self.host = host
        self.port = port
        self.pieces = pieces
        
        self.unchoke = unchoke
        self.connected = connected
        self.interested = interested
        
        self.stop = False

    def start(self):
        try:
            threading.Thread(target = self.reEvaluteTopPeers).start()
            threading.Thread(target = self.optimisticallyUnchoke).start()
            
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((self.host, self.port))
            server.listen(5)
            print(f"Peer server: started on {self.host}:{self.port}")
            while not self.stop:
                client_socket, addr = server.accept()
                if not self.stop:
                    self.connected[addr] = 0 # add connected peer to dict (key = (ip, port), value = downloadRate)
                    thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                    thread.start()
            server.close()
            print("Peer server stopped.")
        except Exception as e:
            print(f"\033[1;31m{f"ERROR IN START: {e}"}\033[0m")

    def handle_client(self, client_socket, addr):
        try:
            # Get ip address and port number of client
            request = client_socket.recv(1024).decode("utf-8")
            print(f"Peer server: Received request: {request}")
            if ("REQUEST_PIECE" in request) and (addr in self.unchoke):
                _, piece_index = request.split("::")
                piece_index = int(piece_index)
                if piece_index < len(self.pieces):
                    print(f"Peer server: Sending piece {piece_index}")
                    client_socket.send(self.pieces[piece_index])
            client_socket.close()
        except Exception as e:
            print(f"\033[1;31m{f"ERROR IN HANDLE CLIENT: {e}"}\033[0m")
        
    def stop(self):
        self.stop = True
        # Tạo một kết nối giả để thoát khỏi accept() và dừng vòng lặp
        try:
            stop_socket = socket.create_connection((self.host, self.port))
            stop_socket.close()
        except Exception as e:
            print(f"\033[1;31m{f"ERROR STOP: {e}"}\033[0m")
    
    def reEvaluteTopPeersBody(self):
        try:
            self.unchoke = []
            firstPriority = {}
            for key in self.interested:
                if key in self.connected:
                    firstPriority[key] = self.connected[key]
            lengthOfFirstPriority = len(firstPriority)
            if lengthOfFirstPriority == MAX_REGULAR_UNCHOKE:
                self.unchoke += list(firstPriority.keys())
            elif lengthOfFirstPriority < MAX_REGULAR_UNCHOKE:
                self.unchoke += list(firstPriority.keys())
                sortedConnected = sorted(self.connected.items(), key = lambda item: item[1], reverse = True)
                for peer, _ in sortedConnected:
                    if peer in self.unchoke:
                        continue
                    self.unchoke.append(peer)
                    if len(self.unchoke) == MAX_REGULAR_UNCHOKE:
                        break
            else:
                sortedFirstPriority = sorted(firstPriority.items(), key = lambda item : item[1], reverse = True)
                self.unchoke = [peer[0] for peer in sortedFirstPriority[: MAX_REGULAR_UNCHOKE]]
        except Exception as e:
            print(f"\033[1;31m{f"ERROR IN REEVALUTE BODY: {e}"}\033[0m")

    def reEvaluteTopPeers(self):
        try:
            t0 = threading.Thread(target = self.reEvaluteTopPeersBody)
            t0.start()
            t0.join()
            t = threading.Timer(REGULAR_UNCHOKE, self.reEvaluteTopPeersBody)
            while not self.stop:
                t.start()
                t.join()
                t = threading.Timer(REGULAR_UNCHOKE, self.reEvaluteTopPeersBody)
        except Exception as e:
            print(f"\033[1;31m{f"ERROR IN REEVALUTE: {e}"}\033[0m")

    def optimisticallyUnchokeBody(self):
        try:
            if len(self.connected) > MAX_REGULAR_UNCHOKE:
                connectedKeys = list(self.connected.keys())
                randomPeer = random.choice(connectedKeys)
                while randomPeer in self.unchoke:
                    pass
                self.unchoke.append(randomPeer)
        except Exception as e:
            print(f"\033[1;31m{f"ERROR IN OPTIMISTICALLY BODY: {e}"}\033[0m")
            
    def optimisticallyUnchoke(self):
        try:
            t0 = threading.Thread(target = self.optimisticallyUnchokeBody)
            t0.start()
            t0.join()
            t = threading.Timer(OPTIMISTICALLY_UNCHOKE, self.optimisticallyUnchokeBody)
            while not self.stop:
                t.start()
                t.join()
                t = threading.Timer(OPTIMISTICALLY_UNCHOKE, self.optimisticallyUnchokeBody)
        except Exception as e:
            print(f"\033[1;31m{f"ERROR IN OPTIMISTICALLY: {e}"}\033[0m")
    
    def updateDownloadRateForPeer(self, addr, rate = 0):
        if addr in self.connected:
            self.connected[addr] = rate
        self.interested[addr] = rate
    
    def resetDownloadRate(self):
        for key in self.connected:
            self.connected[key] = 0
        for key in self.interested:
            self.interested[key] = 0