import threading
import random
import socket
from split import get_piece
import json
import struct


MAX_REGULAR_UNCHOKE = 4
REGULAR_UNCHOKE = 10
OPTIMISTICALLY_UNCHOKE = 30
MAX_CONNECTION = 15


from datetime import datetime

def time_transfer(time): 
    # Chuỗi thời gian ISO 8601
    # Chuyển đổi chuỗi sang đối tượng datetime
    # Chuyển đổi chuỗi sang đối tượng datetime
    dt = datetime.fromisoformat(time.replace("Z", "+00:00"))

    # Chuyển đổi đối tượng datetime thành timestamp (giây)
    creationDate = int(dt.timestamp() * 1000)  # Nhân với 1000 để có mili giây
    return creationDate


def package_data(data, index): 
    data_length = len(data)
    packed_header = struct.pack('ii', index, data_length)  # 2 số nguyên
    packed_data = packed_header + data  # Nối header với data
    return packed_data


def mappingFromListToDict(interested: list) -> dict:
    result: dict = {}
    try:
        for peer in interested:
            result[peer['ip']] = 0
        return result
    except Exception as e:
        print(f"\033[1;31m{f"ERROR IN MAPPING: {e}"}\033[0m")
        return {}
class P2PUploader:
    def __init__(self,metainfo, host: str, port: int, pieces: list = [], interested: list = []):
        self.host = host
        self.port = port
        self.pieces = pieces
        
        self.unchoke = []
        self.connected = {}
        self.interested = mappingFromListToDict(interested=interested)
        
        self.running = True
        self.status_file = "status.txt"

        self.creationDate = time_transfer(metainfo["creationDate"])
        self.metainfo = metainfo

    def start(self):
        try:
            threading.Thread(target = self.reEvaluteTopPeers).start()
            threading.Thread(target = self.optimisticallyUnchoke).start()
            
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((self.host, self.port))
            server.listen(5)
            print(f"Peer server: started on {self.host}:{self.port}")
            while self.running:
                client_socket, addr = server.accept()
                if self.running:
                    print(f"\033[1;32m{addr}\033[0m")
                    self.connected[addr[0]] = 0 # add connected peer to dict (key = (ip, port), value = downloadRate)
                    if (len(self.unchoke) < MAX_REGULAR_UNCHOKE) and (addr[0] not in self.unchoke):
                        self.unchoke.append(addr[0])
                    thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                    thread.start()
                    print(f"{self.port}\n{self.unchoke}\n{self.connected}")
            server.close()
            print("Peer server stopped.")
        except Exception as e:
            print(f"\033[1;31m{f"ERROR IN START: {e}"}\033[0m")

    def handle_client(self, client_socket, addr):
        try:
            # Get ip address and port number of client
            request = client_socket.recv(1024).decode("utf-8")
            print(f"Peer server {self.port}: Received request: {request}")
            if ("REQUEST_PIECE::" in request) and (addr[0] in self.unchoke):
                _, piece_index = request.split("::")
                piece_index = int(piece_index)
                # if piece_index < len(self.pieces):
                print(f"Peer server {self.port}: Sending piece {piece_index}")
                # client_socket.send(get_piece(index=piece_index))
                # piece_data = next((piece.data for piece in self.pieces if piece.index == piece_index), None)
                try: 
                    print(type(piece_index), piece_index, self.creationDate)
                    piece_data = get_piece(index=piece_index, creationDate=self.creationDate, metainfo=self.metainfo)

                    print(len(piece_data))
                    if piece_data:
                        try:
                            data = package_data(piece_data, piece_index)
                            client_socket.send(data)
                        except Exception as e:
                            print(f"\033[1;31m{f"ERROR IN HANDLE CLIENT SEND PIECE: {e}"}\033[0m")
                        # print('test', piece_data)``
                    else:
                        try:
                            client_socket.send(b"")  # Send an empty response if the piece isn't found
                        except Exception as e:
                            print(f"\033[1;31m{f"ERROR IN HANDLE CLIENT SEND PIECE EMPTY: {e}"}\033[0m")
                except Exception as e: print("here ", e)
                # elif ("REQUEST_PIECES" in request):
                #     pass
            elif "REQUEST_PIECES" in request:
                # Trả về danh sách các chỉ số mảnh mà server sở hữu
                try:
                    with open(f"status/{self.creationDate}.txt", "r") as f:
                        downloaded = json.loads(f.read())
                    # piece_indices = [piece.index for piece in self.pieces]
                    # client_socket.send(",".join(map(str, piece_indices)).encode("utf-8"))
                    client_socket.send(",".join(map(str, downloaded)).encode("utf-8"))
                except Exception as e:
                    print(f"\033[1;31m{f"ERROR IN READ STATUS (UPLOAD): {e}"}\033[0m")        
            # client_socket.close()
            # self.connected.pop(addr)
            else:
                print("else")
        except Exception as e:
            print(f"\033[1;31m{f"ERROR IN HANDLE CLIENT: {e}"}\033[0m")
        finally:
            # print("close")
            # client_socket.close()
            try:
                if self.connected[addr[0]]:
                    self.connected.pop(addr[0])
            except Exception as e:
                print(f"\033[1;31m{f"ERROR IN HANDLE CLIENT REMOVE: {e}"}\033[0m")
        
    def stop(self):
        self.running = False
        # Tạo một kết nối giả để thoát khỏi accept() và dừng vòng lặp
        try:
            stop_socket = socket.create_connection((self.host, self.port))
            stop_socket.close()
        except Exception as e:
            print(f"\033[1;31m{f"ERROR IN STOP: {e}"}\033[0m")
    
    def reEvaluteTopPeersBody(self):
        if (not self.running) or (not len(self.connected)):
            return
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
            while self.running:
                t.start()
                t.join()
                t = threading.Timer(REGULAR_UNCHOKE, self.reEvaluteTopPeersBody)
        except Exception as e:
            print(f"\033[1;31m{f"ERROR IN REEVALUTE: {e}"}\033[0m")

    def optimisticallyUnchokeBody(self):
        if not self.running:
            return
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
            while self.running:
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