import socket
import json
import requests
import sseclient
import threading
import state as var
from fetch_api import * 
from config import HOST


# list peers to connect 
PeersList = []

# list metainfo file for multiple download 
Metainfo = []  

stop_event = threading.Event()

def getLocalIP():
    # Lấy tên host của máy
    hostname = socket.gethostname()
    # Lấy địa chỉ IP cục bộ
    local_ip = socket.gethostbyname(hostname)
    return local_ip


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
        print("You join successfully!")

        # create a thread to listen to notification from tracker 
        subscribe_channel(code)
    else: 
        print(f"\033[1;31m{response.get('message')}\033[0m")



async def main(): 
    await get('e3f4b4aed9c346c76bab6afa60fd6d5198164797')


if __name__ == '__main__':
    asyncio.run(main()) 