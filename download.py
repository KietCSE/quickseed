import socket
import os
import hashlib
import threading
from mockServer import MockPeerServer
from file import File, Piece

class P2PDownloader:
    def __init__(self, file: File, list_peer):
        self.file = file
        self.list_peer = list_peer
        self.piece_size = file.piece_size

    def connect_to_peer(self, peer):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((peer['ip'], peer['port']))
        return sock

    def download_piece(self, sock, piece_index):
        sock.send(f"REQUEST_PIECE::{piece_index}".encode("utf-8"))
        data = sock.recv(self.piece_size)
        return data

    def verify_piece(self, piece_data, piece_index):
        """Kiểm tra tính toàn vẹn của piece với hash SHA-1."""
        piece_hash = hashlib.sha1(piece_data).hexdigest()
        print(f"Computed hash for piece {piece_index}: {piece_hash}")
        return piece_hash == self.file.piece_hash[piece_index]

    def download_directory(self):
        """Quản lý việc tải từng file trong thư mục."""
        # Tạo file trống với kích thước cố định cho mỗi file
        self.file._initialize_empty_files()

        # Tiến hành tải từng mảnh cho mỗi file trong thư mục
        for piece_index in range(self.file.num_pieces):
            piece_verified = False

            # Nếu piece đã được tải xong, bỏ qua
            if piece_index in self.file.piece_idx_downloaded:
                continue

            # Gửi yêu cầu đến từng peer để tải mảnh dữ liệu
            for peer in self.list_peer:
                try:
                    sock = self.connect_to_peer(peer)
                    piece_data = self.download_piece(sock, piece_index)

                    # Xác thực và ghi piece vào file tương ứng nếu dữ liệu hợp lệ
                    if self.verify_piece(piece_data, piece_index):
                        piece = Piece(piece_data, piece_index)
                        self.file.add_piece(piece)
                        print(f"Client: Downloaded piece {piece_index} from peer {peer}")
                        piece_verified = True
                        sock.close()
                        break  # Dừng nếu đã tải thành công piece từ một peer
                    else:
                        print(f"Client: Piece {piece_index} from {peer} failed integrity check.")
                    sock.close()
                except Exception as e:
                    print(f"Error downloading piece {piece_index} from {peer}: {e}")
                    continue  # Thử tải từ peer tiếp theo nếu xảy ra lỗi

            if not piece_verified:
                print(f"Client: Failed to download valid piece {piece_index}. Retrying...")

        # Kiểm tra xem tất cả các piece đã tải xong chưa
        if len(self.file.piece_idx_downloaded) == self.file.num_pieces:
            print("Client: Directory download completed.")
        else:
            missing_pieces = set(range(self.file.num_pieces)) - set(self.file.piece_idx_downloaded)
            print("Client: Download incomplete. Missing pieces:", missing_pieces)

# Cấu hình kích thước và dữ liệu cho từng mảnh
new_piece_size = 2048
new_pieces = [
    b"X" * new_piece_size,
    b"Y" * new_piece_size,
    b"Z" * new_piece_size,
    b"W" * new_piece_size
]  # Bốn mảnh với kích thước 2048 byte mỗi mảnh

# Khởi tạo server peer với dữ liệu mới
new_peer_server = MockPeerServer("127.0.0.1", 6000, new_pieces)
new_server_thread = threading.Thread(target=new_peer_server.start)
new_server_thread.start()

# Hash cho từng mảnh dữ liệu để mô phỏng việc kiểm tra tính toàn vẹn
new_piece_hashes = [
    hashlib.sha1(new_pieces[0]).hexdigest(),
    hashlib.sha1(new_pieces[1]).hexdigest(),
    hashlib.sha1(new_pieces[2]).hexdigest(),
    hashlib.sha1(new_pieces[3]).hexdigest()
]

# Metainfo mới để mô phỏng file lớn hơn
new_metainfo = {
    "info": {
        "piece length": new_piece_size,
        "length": new_piece_size * 4,  # Giả sử folder có 4 pieces, mỗi piece 2048 byte
        "name": "large_file.txt",
        "pieces": new_piece_hashes
    },
    "files": [
        {
        "length": 4096,
        "path": ["folder1", "file1.txt"]
        },
        {
        "length": 4096,
        "path": ["folder2", "subfolder", "file2.txt"]
        }
    ]  
}

# Danh sách peer giả với nhiều peer đang chạy
new_list_peer = [
    {"ip": "127.0.0.1", "port": 6000},
    {"ip": "127.0.0.1", "port": 6001}
]

# Khởi tạo đối tượng File và P2PDownloader rồi tiến hành tải
new_file = File(new_metainfo)
new_downloader = P2PDownloader(new_file, new_list_peer)
new_downloader.download_directory()

# Dừng các server sau khi tải xong
new_peer_server.stop()
new_server_thread.join()
