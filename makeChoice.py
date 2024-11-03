import heapq
import random
class PieceInfo:
    """Thông tin về một mảnh và các peer sở hữu nó."""
    def __init__(self, piece_index):
        self.piece_index = piece_index
        self.peers = []  # Tập hợp các peer sở hữu mảnh này

    def add_peer(self, peer):
        """Thêm peer sở hữu mảnh này."""
        self.peers.append(peer)

    def remove_peer(self, peer):
        """Xóa peer khỏi danh sách sở hữu mảnh này."""
        if peer in self.peers:
            self.peers.remove(peer)

    def get_random_peer(self):
        """Lấy ngẫu nhiên một peer từ danh sách sở hữu mảnh."""
        return next(iter(self.peers)) if self.peers else None
    def __str__(self):
        return f"Piece {self.piece_index}: Peers: {self.peers}"

class PieceQueue:
    """Hàng đợi các mảnh theo chiến lược 'rarest first'."""
    def __init__(self):
        self.piece_info_dict = {}  # Map từ chỉ số mảnh đến đối tượng PieceInfo
        self.piece_queue = []  # Hàng đợi ưu tiên các mảnh theo số lượng peer ít nhất

    def add_piece(self, piece_index, peer):
        """Thêm thông tin sở hữu mảnh từ một peer."""
        if piece_index not in self.piece_info_dict:
            self.piece_info_dict[piece_index] = PieceInfo(piece_index)
        self.piece_info_dict[piece_index].add_peer(peer)

    def build_queue(self):
        """Xây dựng hàng đợi ưu tiên theo số lượng peer ít nhất cho mỗi mảnh."""
        if self.piece_queue: 
            self.piece_queue.clear()
        for piece_info in self.piece_info_dict.values():
            if piece_info.peers:  # Chỉ thêm các mảnh có peers hợp lệ
                self.piece_queue.append((len(piece_info.peers), piece_info.piece_index))
        
        # for piece_count, piece_index in self.piece_queue:
        #     piece_info = self.piece_info_dict[piece_index]
        #     print(piece_info)
        heapq.heapify(self.piece_queue)


    def get_rarest_piece_and_peer(self):
        """Lấy mảnh có số lượng peer ít nhất và peer sở hữu nó."""
        while self.piece_queue:
            _, piece_index = heapq.heappop(self.piece_queue)
            piece_info = self.piece_info_dict.get(piece_index)
            if piece_info:
                peer = piece_info.peers[random.randint(0, len(piece_info.peers) - 1)]
                if peer:
                    return piece_index, peer
        return None, None  # Trả về None nếu không còn mảnh hoặc peer hợp lệ

    def __str__(self): return '\n'.join([str(self.piece_info_dict[piece_index]) for _, piece_index in self.piece_queue])