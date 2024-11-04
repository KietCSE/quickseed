import socket
import json
import requests
import sseclient
import threading
import bencodepy
import state as var
from fetch_api import * 
from config import HOST
from download import *
from upload import *
from config import TEST
# list peers to connect 
PeersList = []

# list metainfo file for multiple download 
Metainfo = {}  

ListHashPeer = []
# using only one for testing


def time_transfer(time): 
    # Chuỗi thời gian ISO 8601
    # Chuyển đổi chuỗi sang đối tượng datetime
    # Chuyển đổi chuỗi sang đối tượng datetime
    dt = datetime.fromisoformat(time.replace("Z", "+00:00"))

    # Chuyển đổi đối tượng datetime thành timestamp (giây)
    creationDate = int(dt.timestamp() * 1000)  # Nhân với 1000 để có mili giây
    return creationDate


stop_event = threading.Event()


def getLocalIP():
    try:
        # Kết nối tạm đến một IP và cổng không thật sự gửi dữ liệu để xác định IP LAN
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Kết nối đến một IP ngoài (Google DNS server) để lấy địa chỉ IP của mạng LAN
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception as e:
        print(f"Lỗi khi lấy IP: {e}")
        return None


def decode_bencoded(data):
    # Giải mã dữ liệu bencoded
    decoded_data = bencodepy.decode(data)

    # Chuyển đổi kiểu dữ liệu từ bytes sang str
    return convert_bytes_to_str(decoded_data)


def convert_bytes_to_str(data):
    # Nếu là từ điển, duyệt qua từng phần tử
    if isinstance(data, dict):
        return {key.decode('utf-8'): convert_bytes_to_str(value) for key, value in data.items()}
    # Nếu là danh sách, duyệt qua từng phần tử
    elif isinstance(data, list):
        return [convert_bytes_to_str(item) for item in data]
    # Nếu là kiểu dữ liệu khác (chẳng hạn int), trả về trực tiếp
    elif isinstance(data, bytes):
        return data.decode('utf-8')  # Chuyển đổi bytes sang str
    else:
        return data


# create long-live http connection for server sent event (SSE) to tracker 
def subscribe_worker(code): 
    global PeersList
    if TEST:
        print("Start subcribe worker")
    url = f'{HOST}/subscribe/{var.PEER_ID}/{code}'  
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Kiểm tra mã trạng thái HTTP

        # Sử dụng sseclient để xử lý sự kiện từ SSE
        client = sseclient.SSEClient(response)

        # Lắng nghe sự kiện và xử lý
        for event in client.events():
            PeersList = event.data
            # PeersList = [peer for peer in PeersList if isinstance(peer, dict) and str(peer.get("peerId")) != str(var.PEER_ID)]
            PeersList = json.loads(PeersList)
            # for peer in PeersList: print((peer))
            if TEST:
                print(PeersList)
                print(type(PeersList))

            # PeersList = list(filter(lambda x: str(x["peerId"]) != str(var.PEER_ID), PeersList))

    except requests.exceptions.RequestException as e:
        print(f"Error with server connection: {e}")
        print(f"Detailed error info: {e.__class__.__name__}: {e}")



# create a threat to listen to notification from tracker when a new peer join network 
def subscribe_channel(code):
    thread = threading.Thread(target=subscribe_worker, args=(code,))
    thread.start()


# join torrent network in tracker and receive a list of peer + metainfo file
async def get(code): 
    var.STATUS = 'leecher'
    global PeersList
    data = {
        "hashCode": code,
        "peerId": var.PEER_ID,
        "port": var.PORT,
        "uploaded": var.UPLOADED,
        "downloaded": var.DOWNLOADED,
        "left": var.LEFT,
        "compact": "1",
        "status": var.STATUS,
        "numwant": "50",
        "ip": getLocalIP(),
    }
    response = await postAPI(f'{HOST}/join', data)
    if (response.get("status")): 

        PeersList = response.get('peers')
        # PeersList = json.loads(PeersList)
        PeersList = [peer for peer in PeersList if isinstance(peer, dict) and str(peer.get("peerId")) != str(var.PEER_ID)]

        if TEST:
            print(PeersList)
            print(type(PeersList))
        

        Metainfo = response.get("metainfo")
        filename = time_transfer(Metainfo['creationDate'])
        path_file = f'status/{filename}.txt'
        target_dir = os.path.dirname(path_file)  # Lấy đường dẫn thư mục của target_file
        os.makedirs(target_dir, exist_ok=True) 
        
        if not os.path.exists(path_file):
            with open(path_file, 'w') as f:
                f.write("[]")
            if TEST:
                print("Da tao file status")
        else: 
            # print("dat ton tai file status")
            print(f"\033[1;31m{'DA TON TAI FILE STATUS'}'\033[0m")


        # if BENCODE: Metainfo = decode_bencoded(Metainfo)
        # print(Metainfo)
        hashpieces = Metainfo["info"]["pieces"]
        ListHashPeer = [hashpieces[i:i + 40] for i in range(0, len(hashpieces), 40)]
        # print(ListHashPeer)
        # print("You join successfully!")
        print(f"\033[1;34m{'YOU JOINED SUCCESSFULLY'}\033[0m")

        # create a thread to listen to notification from tracker 
        subscribe_channel(code)
        threading.Thread(target=P2PUploader(metainfo=Metainfo, host="0.0.0.0", port=var.PORT, interested=PeersList).start).start()
        threading.Thread(target=P2PDownloader(file=File(Metainfo), list_peer=PeersList).download_muti_directory).start()
    else: 
        print(f"\033[1;31m{response.get('message')}\033[0m")


async def seed(code): 
    var.STATUS = 'seeder'
    data = {
        "hashCode": code,
        "peerId": var.PEER_ID,
        "port": var.PORT,
        "uploaded": var.UPLOADED,
        "downloaded": var.DOWNLOADED,
        "left": var.LEFT,
        "compact": "1",
        "status": var.STATUS,
        "numwant": "50",
        "ip": getLocalIP(),
    }
    response = await postAPI(f'{HOST}/join', data)
    if (response.get("status")): 
        PeersList = response.get('peers')
        PeersList = [peer for peer in PeersList if isinstance(peer, dict) and str(peer.get("peerId")) != str(var.PEER_ID)]
        if TEST:
            print(PeersList)

            print(type(PeersList))
        Metainfo = response.get('metainfo')
        # if BENCODE: Metainfo = decode_bencoded(Metainfo)
        # print(Metainfo)
        hashpieces = Metainfo["info"]["pieces"]
        ListHashPeer = [hashpieces[i:i + 40] for i in range(0, len(hashpieces), 40)]
        # print(ListHashPeer)
        # print("You join successfully!")
        # print(f"\033[1;34m{'YOU JOINED SUCCESSFULLY'}\033[0m")


        # create a thread to listen to notification from tracker 
        subscribe_channel(code)
        
        # P2PDownloader(file=File(Metainfo), list_peer=PeersList).download_muti_directory()
        threading.Thread(target=P2PUploader(metainfo=Metainfo, host="0.0.0.0", port=var.PORT, interested=PeersList).start).start()
        print('You are seeding for other peers...')
    else: 
        print(f"\033[1;31m{response.get('message')}\033[0m")