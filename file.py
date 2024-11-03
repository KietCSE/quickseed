import os
import math
from split import save_piece
import json
from datetime import datetime
def time_transfer(time): 
    # Chuỗi thời gian ISO 8601
    # Chuyển đổi chuỗi sang đối tượng datetime
    # Chuyển đổi chuỗi sang đối tượng datetime
    dt = datetime.fromisoformat(time.replace("Z", "+00:00"))

    # Chuyển đổi đối tượng datetime thành timestamp (giây)
    creationDate = int(dt.timestamp() * 1000)  # Nhân với 1000 để có mili giây
    return creationDate

# # Hàm xử lý kết nối từ client
# def handle_client(client_socket):
#     with client_socket:
#         while True:
#             # Đọc header (2 số nguyên)
#             header = client_socket.recv(8)  # 2 số nguyên (4 byte mỗi số)
#             if not header:
#                 break

#             index, data_length = struct.unpack('ii', header)

#             # Đọc data theo length đã nhận
#             data = bytearray()
#             while len(data) < data_length:
#                 packet = client_socket.recv(data_length - len(data))  # Đọc phần còn lại
#                 if not packet:
#                     break  # Nếu không còn dữ liệu, thoát
#                 data.extend(packet)  # Thêm phần đã nhận vào dữ liệu


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


class Piece:
    def __init__(self, data: bytes, index: int):
        self.index = index
        self.data = data

class File:
    def __init__(self, meta_info):
        self.path = meta_info['info']['name']
        self.piece_size = meta_info['info']['pieceLength']
        self.files = meta_info["info"]['files']
        self.total_size = sum(file['length'] for file in self.files)
        self.num_pieces = math.ceil(self.total_size / self.piece_size)
        self.piece_hash = meta_info['info']['pieces']
        self.creationDate = time_transfer(meta_info['creationDate'])
        # Lưu trữ danh sách các mảnh đã và chưa tải xuống
        self.pieces = []
        self.piece_idx_downloaded = []
        self.piece_idx_not_downloaded = list(range(self.num_pieces))

        # Đường dẫn tới file lưu trạng thái tải xuống
        self.status_file = f'status/{self.creationDate}.txt'

        # Tạo thư mục gốc và các file trống trong cấu trúc thư mục
        # self._initialize_empty_files()
        self.metainfo = meta_info

    def _initialize_empty_files(self):
        """Tạo cấu trúc thư mục và các file chỉ cho các mảnh chưa tải."""
        for file_info in self.files:
            file_path = os.path.join(self.path, *file_info['path'])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Kiểm tra và mở file ở chế độ "a+b" (ghi bổ sung) nếu nó đã tồn tại
            if os.path.exists(file_path):
                with open(file_path, "a+b") as f:
                    existing_size = os.path.getsize(file_path)
                    
                    # Nếu kích thước của file nhỏ hơn kích thước yêu cầu, mở rộng đến kích thước cần thiết
                    if existing_size < file_info['length']:
                        f.seek(file_info['length'] - 1)
                        f.write(b'\0')  # Mở rộng file đến kích thước yêu cầu

                    # Đánh dấu các mảnh đã tải dựa vào kích thước hiện tại
                    piece_start = 0
                    while piece_start < existing_size:
                        piece_index = piece_start // self.piece_size
                        self.piece_idx_downloaded.append(piece_index)
                        piece_start += self.piece_size

            # Nếu file chưa tồn tại, tạo mới với kích thước cố định
            else:
                with open(file_path, "wb") as f:
                    f.truncate(file_info['length'])


    def load_downloaded_status(self):
        """Đọc danh sách các piece đã tải từ file trạng thái."""
        if os.path.exists(self.status_file):
            with open(self.status_file, "r") as f:
                # line = f.readline().strip()
                    line = json.loads(f.read())
                # if line.startswith("downloaded_pieces = "):
                    # pieces_str = line.split(" = ")[1].strip()
                    
                    # Kiểm tra nếu pieces_str rỗng hoặc chỉ chứa "[]"
                    if len(line) == 0:
                        self.piece_idx_downloaded = []
                    else:
                        self.piece_idx_downloaded = line

                    # Xác định các piece chưa được tải
                    self.piece_idx_not_downloaded = [i for i in range(self.num_pieces) if i not in self.piece_idx_downloaded]


    def save_downloaded_status(self):
        """Ghi danh sách các piece đã tải xuống vào file trạng thái."""
        # target_dir = os.path.dirname(self.)  # Lấy đường dẫn thư mục của target_file
            # os.makedirs(target_dir, exist_ok=True)
        with open(self.status_file, "w") as f:
            downloaded = sorted(self.piece_idx_downloaded)
            json.dump(downloaded, f)

    def add_piece(self, piece: Piece):
        """Thêm mảnh dữ liệu vào file tương ứng trong thư mục."""
        if piece.index in self.piece_idx_not_downloaded:
            self.pieces.append(piece)
            self.piece_idx_downloaded.append(piece.index)
            self.piece_idx_not_downloaded.remove(piece.index)
            # self.write_piece_to_file(piece)
            save_piece(data=piece.data, index=piece.index, creationDate=self.creationDate, metainfo=self.metainfo)

    def write_piece_to_file(self, piece: Piece):
        """Ghi dữ liệu vào file đúng vị trí trong cấu trúc thư mục."""
        offset = piece.index * self.piece_size 
        remaining_data = piece.data
        
        for file_info in self.files:
            file_path = os.path.join(self.path, *file_info['path'])
            file_length = file_info['length']
            
            # Xác định nếu dữ liệu của piece nằm trong file này
            if offset < file_length:
                with open(file_path, "r+b") as f:
                    f.seek(offset)
                    write_data = remaining_data[:file_length - offset]
                    f.write(write_data)
                    remaining_data = remaining_data[len(write_data):]
                
                if not remaining_data:
                    break

            offset = max(0, offset - file_length)

    def is_download_complete(self):
        """Kiểm tra xem tất cả các mảnh đã được tải xuống chưa."""
        return len(self.piece_idx_downloaded) == self.num_pieces
