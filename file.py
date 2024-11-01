import os
import math

class Piece:
    def __init__(self, data: bytes, index: int):
        self.index = index
        self.data = data

class File:
    def __init__(self, meta_info):
        self.path = meta_info['info']['name']
        self.piece_size = meta_info['info']['piece length']
        self.files = meta_info['files']
        self.total_size = sum(file['length'] for file in self.files)
        self.num_pieces = math.ceil(self.total_size / self.piece_size)
        self.piece_hash = meta_info['info']['pieces']
        
        # Lưu trữ danh sách các mảnh đã và chưa tải xuống
        self.pieces = []
        self.piece_idx_downloaded = []
        self.piece_idx_not_downloaded = list(range(self.num_pieces))

        # Tạo thư mục gốc và các file trống trong cấu trúc thư mục
        self._initialize_empty_files()

    def _initialize_empty_files(self):
        """Tạo cấu trúc thư mục và file trống với kích thước cố định."""
        for file_info in self.files:
            file_path = os.path.join(self.path, *file_info['path'])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.truncate(file_info['length'])

    def add_piece(self, piece: Piece):
        """Thêm mảnh dữ liệu vào file tương ứng trong thư mục."""
        if piece.index in self.piece_idx_not_downloaded:
            self.pieces.append(piece)
            self.piece_idx_downloaded.append(piece.index)
            self.piece_idx_not_downloaded.remove(piece.index)
            self.write_piece_to_file(piece)

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
