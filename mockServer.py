import socket
import threading
class MockPeerServer:
    def __init__(self, host, port, pieces):
        self.host = host
        self.port = port
        self.pieces = pieces
        self.running = True

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"Peer server: started on {self.host}:{self.port}")
        while self.running:
            client_socket, addr = server.accept()
            thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            thread.start()
        server.close()
        print("Peer server stopped.")

    def handle_client(self, client_socket):
        request = client_socket.recv(1024).decode("utf-8")
        # print(f"Peer server: Received request: {request}")
        if "REQUEST_PIECE"  and "::" in request:
            # Parse the requested piece index
            piece_index = int(request.split("::")[1])
            piece_data = next((piece.data for piece in self.pieces if piece.index == piece_index), None)
            
            if piece_data:
                client_socket.send(piece_data)
            else:
                client_socket.send(b"")  # Send an empty response if the piece isn't found
        elif "REQUEST_PIECES" in request:
            # Trả về danh sách các chỉ số mảnh mà server sở hữu
            piece_indices = [piece.index for piece in self.pieces]
            client_socket.send(",".join(map(str, piece_indices)).encode("utf-8"))

        client_socket.close()
    def stop(self):
        self.running = False
        # Tạo một kết nối giả để thoát khỏi accept() và dừng vòng lặp
        try:
            stop_socket = socket.create_connection((self.host, self.port))
            stop_socket.close()
        except Exception as e:
            print(f"Error stopping server: {e}")


