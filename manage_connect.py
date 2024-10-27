import socket
import threading
import time

class ConnectionManager:
    def __init__(self):
        self.connections = {}  # Lưu trữ kết nối dưới dạng {peer: socket_connection}

    # Hàm thiết lập kết nối TCP tới một peer
    def connect_to_peer(self, peer_ip, peer_port):
        try:
            peer_address = (peer_ip, peer_port)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(peer_address)
                self.connections[peer_address] = s  # Lưu trữ kết nối
                print(f"Connected to peer {peer_ip}:{peer_port}")
                # Bắt đầu xử lý kết nối này (như trao đổi dữ liệu)
                self.handle_peer_connection(s, peer_address)
        except Exception as e:
            print(f"Error connecting to peer {peer_ip}:{peer_port}: {e}")
            return False

    # Hàm để xử lý kết nối giữa peers, có thể là trao đổi dữ liệu, handshake, etc.
    def handle_peer_connection(self, connection, peer_address):
        try:
            while True:
                data = connection.recv(1024)  # Nhận dữ liệu từ peer
                if not data:
                    print(f"Peer {peer_address} disconnected")
                    break
                print(f"Received data from {peer_address}: {data}")
                # Gửi lại dữ liệu hoặc thực hiện các thao tác xử lý khác
                # connection.sendall(b"ACK")  # Ví dụ gửi ACK để xác nhận
        except Exception as e:
            print(f"Error during communication with peer {peer_address}: {e}")
        finally:
            self.close_connection(peer_address)

    # Hàm đóng kết nối với peer
    def close_connection(self, peer_address):
        if peer_address in self.connections:
            try:
                self.connections[peer_address].close()
                print(f"Connection closed with peer {peer_address}")
                del self.connections[peer_address]
            except Exception as e:
                print(f"Failed to close connection with {peer_address}: {e}")

    # Quản lý kết nối đồng thời thông qua multithreading
    def manage_peer_connections(self, peer_list):
        threads = []
        for peer in peer_list:
            peer_ip, peer_port = peer
            t = threading.Thread(target=self.connect_to_peer, args=(peer_ip, peer_port))
            t.start()
            threads.append(t)

        # Đợi tất cả các kết nối hoàn thành
        for t in threads:
            t.join()

    # Kiểm tra và duy trì các phiên kết nối hiện tại
    def maintain_sessions(self):
        while True:
            # Ví dụ, kiểm tra kết nối sau mỗi 30 giây
            print("Checking active connections...")
            for peer, connection in list(self.connections.items()):
                try:
                    connection.sendall(b"KEEP_ALIVE")  # Gửi tín hiệu kiểm tra kết nối
                except Exception as e:
                    print(f"Connection lost with peer {peer}. Error: {e}")
                    self.close_connection(peer)
            time.sleep(30)  # Kiểm tra kết nối sau mỗi 30 giây

