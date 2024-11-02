import socket
import json
import requests
import sseclient
import threading
import bencodepy
import state as var
from fetch_api import * 
from config import HOST
from add_delete_ls import create_metainfo

# list peers to connect 
PeersList = []

# list metainfo file for multiple download 
Metainfo = []  

ListHashPeer = []
# using only one for testing
metainfo = {}


stop_event = threading.Event()


def getLocalIP():
    # Lấy tên host của máy
    hostname = socket.gethostname()
    # Lấy địa chỉ IP cục bộ
    local_ip = socket.gethostbyname(hostname)
    return local_ip


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
            print(PeersList)

    except requests.exceptions.RequestException as e:
        print(f"Error with server connection: {e}")
        print(f"Detailed error info: {e.__class__.__name__}: {e}")



# create a threat to listen to notification from tracker when a new peer join network 
def subscribe_channel(code):
    thread = threading.Thread(target=subscribe_worker, args=(code,))
    thread.start()


# join torrent network in tracker and receive a list of peer + metainfo file
async def get(code): 
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
        Metainfo = response.get('metainfo')
        # if BENCODE: Metainfo = decode_bencoded(Metainfo)
        # print(Metainfo)
        hashpieces = Metainfo["info"]["pieces"]
        ListHashPeer = [hashpieces[i:i + 40] for i in range(0, len(hashpieces), 40)]
        # print(ListHashPeer)
        print("You join successfully!")

        # create a thread to listen to notification from tracker 
        subscribe_channel(code)
    else: 
        print(f"\033[1;31m{response.get('message')}\033[0m")



async def main(): 
    await get('e3f4b4aed9c346c76bab6afa60fd6d5198164797')


if __name__ == '__main__':
    asyncio.run(main()) 