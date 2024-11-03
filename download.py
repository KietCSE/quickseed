import socket
import os
import hashlib
import threading
from split import merge
from mockServer import MockPeerServer
from file import File, Piece
import time
import sys
from tqdm import tqdm
from makeChoice import PieceQueue
from upload import *
# from fetch_api import * 
from config import HOST
# import asyncio
import requests


def call_async_fetchAPI(hashcode):
    loop = asyncio.get_event_loop()
    
    # Tạo task cho hàm bất đồng bộ trong event loop đang chạy
    task = loop.create_task(fetchAPI(f'{HOST}/downloaded/{hashcode}'))

    # Chạy task và lấy kết quả
    return loop.run_until_complete(task)

# import get_seed_peers as gsp

# Hàm xử lý kết nối từ client
def handle_client(client_socket):
    with client_socket:
        while True:
            # Đọc header (2 số nguyên)
            header = client_socket.recv(8)  # 2 số nguyên (4 byte mỗi số)
            if not header:
                break

            index, data_length = struct.unpack('ii', header)
            # Đọc data theo length đã nhận
            data = bytearray()
            while len(data) < data_length:
                packet = client_socket.recv(data_length - len(data))  # Đọc phần còn lại
                if not packet:
                    break  # Nếu không còn dữ liệu, thoát
                data.extend(packet)  # Thêm phần đã nhận vào dữ liệu
            return data

#             # luu du lieu 
#             if BIT_ARRAY[index] == 0: 
#                 save_piece(data, index, Metainfo["creationDate"])  # Thêm data vào tham số
#                 print(f"Đã nhận index: {index} và dữ liệu từ peer.")
#                 BIT_ARRAY[index] = 1
#                 if BIT_ARRAY.all(): 
#                     merge(f'dict/{Metainfo["creationDate"]}', Metainfo["info"]["name"])
#                     save_bitarray(BIT_ARRAY, f"bit{Metainfo["creationDate"]}")
#             else: 
#                 print("piece da co roi")
class P2PDownloader:
    def __init__(self, file: File, list_peer):
        self.file = file
        self.list_peer = list_peer
        self.piece_size = file.piece_size
        self.downloaded_data = 0  # Số byte đã tải xuống
        self.start_time = time.time()  # Ghi lại thời gian bắt đầu 
        self.lock = threading.Lock()
        self.piece_queue = PieceQueue()
        self.num_threads = 5  # Số luồng đồng thời tối đa

        # Nạp trạng thái các piece đã tải từ file trạng thái
        self.file.load_downloaded_status()

    def print_f(self):
        print(self.downloaded_data)

    def connect_to_peer(self, peer):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((peer['ip'], int(peer['port'])))
        return sock
    
    def request_pieces_info(self, sock):
        """Yêu cầu danh sách các mảnh mà peer sở hữu."""
        sock.send("REQUEST_PIECES".encode("utf-8"))
        data = sock.recv(1024*1024)  # Giả định danh sách mảnh sẽ phù hợp với giới hạn này
        pieces_info = list(map(int, data.decode("utf-8").split(",")))
        # print(pieces_info)
        return pieces_info
    
    def collect_piece_availability(self):
        """Thu thập tần suất của các mảnh từ tất cả các peer và xây dựng hàng đợi 'rarest first'."""
        for peer in self.list_peer:
            try:
                sock = self.connect_to_peer(peer)
                peer_pieces = self.request_pieces_info(sock)
                sock.close()

                # Thêm thông tin sở hữu mảnh của mỗi peer vào hàng đợi
                for piece_index in peer_pieces:
                    self.piece_queue.add_piece(piece_index, peer)

            except Exception as e:
                print(f"Error connecting to peer {peer}: {e}")
                continue

        # Xây dựng hàng đợi theo chiến lược "rarest first"
        self.piece_queue.build_queue()
        # print("Piece Queue after building:")
        # for piece_count, piece_index in self.piece_queue.piece_queue:
        #     piece_info = self.piece_queue.piece_info_dict[piece_index]
        #     print(piece_info)


    def download_piece(self, sock, piece_index):
        sock.send(f"REQUEST_PIECE::{piece_index}".encode("utf-8"))
        data = handle_client(sock)
        return data

    def verify_piece(self, piece_data, piece_index):
        """Kiểm tra tính toàn vẹn của piece với hash SHA-1."""
        piece_hash = hashlib.sha1(piece_data).hexdigest()
        # print(f"Computed hash for piece {piece_index}: {piece_hash}")
        # return piece_hash == self.file.piece_hash[piece_index]
        return True

    def download_directory(self, progress_bar):
        while True:
            piece_index, peer = self.piece_queue.get_rarest_piece_and_peer()
            if piece_index is None:
                break  # Hết các mảnh cần tải

            piece_verified = False

            with self.lock:
                if piece_index in self.file.piece_idx_downloaded:
                    continue

            try:
                # print(f"Piece:{piece_index}",peer)
                sock = self.connect_to_peer(peer)
                piece_data = self.download_piece(sock, piece_index)

                if self.verify_piece(piece_data, piece_index):
                    with self.lock:
                        progress_bar.update(len(piece_data))
                        progress_bar.refresh()
                        piece = Piece(piece_data, piece_index)
                        self.file.add_piece(piece)
                        self.downloaded_data += len(piece_data)
                        piece_verified = True

                        self.file.save_downloaded_status()
                        sock.close()
            except Exception as e:
                print(f"Error downloading piece {piece_index} from {peer}: {e}")
                continue

            # Nếu mảnh không hợp lệ, đưa lại vào hàng đợi để thử tải lại
            if not piece_verified:  
                with self.lock:
                    self.piece_queue.add_piece(piece_index, peer)


    def download_muti_directory(self):
        # Thu thập thông tin mảnh và peer
        self.collect_piece_availability()
        # Tính tổng kích thước của các mảnh đã tải
        downloaded_size = sum(self.file.piece_size for _ in self.file.piece_idx_downloaded)
        self.downloaded_data = downloaded_size  # Cập nhật lại tổng dữ liệu đã tải

        # Tạo thanh tiến trình tổng thể
        with tqdm(total=self.file.total_size, unit="B", unit_scale=True, desc="Downloading") as progress_bar:
            progress_bar.update(downloaded_size)
            # Tạo các luồng để tải xuống các mảnh song song
            threads = []
            for _ in range(self.num_threads):
                thread = threading.Thread(target=self.download_directory, args=(progress_bar,))
                threads.append(thread)
                thread.start()

            # Đợi cho tất cả các luồng hoàn thành
            for thread in threads:
                thread.join()
        # progress_bar.close()
        # Kiểm tra nếu tất cả các mảnh đã được tải thành công
        with self.lock:
            if len(self.file.piece_idx_downloaded) == self.file.num_pieces:
                print("Client: Directory download completed.")

                response = requests.get(f'{HOST}/downloaded/{self.file.metainfo["hashCode"]}')
                print(response.json())

                try:
                    merge(f'dict/{self.file.creationDate}', self.file.metainfo['info']['name'])
                except Exception as e:
                    print(f"\033[1;31m{f"ERROR IN MERGE: {e}"}\033[0m")
            else:
                missing_pieces = set(range(self.file.num_pieces)) - set(self.file.piece_idx_downloaded)
                print("Client: Download incomplete. Missing pieces:", missing_pieces)



# # Cấu hình kích thước và dữ liệu cho từng mảnh của nhiều peer
# piece_size = 1024
# pieces_peer1 = [Piece(b"A" * piece_size, 0), Piece(b"B" * piece_size, 1), Piece(b"C" * piece_size, 2), Piece(b"D" * piece_size, 3)]
# pieces_peer2 = [Piece(b"C" * piece_size, 2), Piece(b"D" * piece_size, 3), Piece(b"E" * piece_size, 4), Piece(b"F" * piece_size, 5)]
# pieces_peer3 = [Piece(b"C" * piece_size, 2), Piece(b"D" * piece_size, 3), Piece(b"E" * piece_size, 4), Piece(b"F" * piece_size, 5)]

# import threading

# # Danh sách thông tin cho các peer (IP, cổng và mảnh dữ liệu tương ứng)
# list_peers = [
#     {"ip": "127.0.0.1", "port": 5000, "pieces": pieces_peer1},
#     {"ip": "127.0.0.1", "port": 5001, "pieces": pieces_peer2},
#     {"ip": "127.0.0.1", "port": 5002, "pieces": pieces_peer3}
# ]

# # Tạo các đối tượng server và thread cho từng peer
# peer_servers = []
# server_threads = []

# for info in list_peers:
#     peer_server = P2PUploader(host=info["ip"], port=info["port"], pieces=info["pieces"])
#     # peer_server = P2PUploader()
#     peer_servers.append(peer_server)
    
#     server_thread = threading.Thread(target=peer_server.start)
#     server_threads.append(server_thread)
    
#     # Bắt đầu chạy server
#     server_thread.start()

# # Mã băm cho mỗi mảnh để mô phỏng tính toàn vẹn
# piece_hashes = [
#     hashlib.sha1(pieces_peer1[0].data).hexdigest(),
#     hashlib.sha1(pieces_peer1[1].data).hexdigest(),
#     hashlib.sha1(pieces_peer1[2].data).hexdigest(),
#     hashlib.sha1(pieces_peer1[3].data).hexdigest(),
#     hashlib.sha1(pieces_peer2[2].data).hexdigest(),
#     hashlib.sha1(pieces_peer2[3].data).hexdigest(),
# ]

# # Metainfo giả lập cấu trúc thư mục với hai tệp có nhiều mảnh
# metainfo = {
#     "creationDate": 12345678,
#     "info": {
#         "piece length": piece_size,
#         "length": piece_size * 6,
#         "name": "multi_peer_test_file.txt",
#         "pieces": piece_hashes,
#     },
#     "files": [
#         {"length": int(piece_size*2.5), "path": ["folder", "file1.txt"]},
#         {"length": int(piece_size*3.5), "path": ["folder", "file2.txt"]}
#     ]
# }

# peersList = [
#     {"ip": "127.0.0.1", "port": 5000,},
#     {"ip": "127.0.0.1", "port": 5001},
#     {"ip": "127.0.0.1", "port": 5002}
# ]

# # Khởi tạo đối tượng File và P2PDownloader và bắt đầu tải xuống
# file = File(metainfo)
# downloader = P2PDownloader(file, peersList)
# downloader.download_muti_directory()

# # Đóng các server sau khi hoàn tất tải xuống
# # for peer_server in peer_servers:
# #     peer_server.stop()

# for server_thread in server_threads:
#     server_thread.join()

# # # In kết quả kiểm tra
# P2PDownloader.print_f(downloader)
