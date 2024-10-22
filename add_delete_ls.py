import os
import time
import json
import hashlib
from fetch_api import *
from config import HOST
# import bencodepy

def hashSHA1(obj):
    """Hash một đối tượng Python bằng thuật toán SHA-1."""
    # Chuyển đổi đối tượng thành chuỗi JSON
    json_string = json.dumps(obj, sort_keys=True).encode()  # Mã hóa thành bytes
    # Tạo hash SHA-1
    sha1_hash = hashlib.sha1(json_string).hexdigest()  # Chuyển đổi sang chuỗi hex
    return sha1_hash


def get_file_info(path):
    file_info = []
    if os.path.isdir(path):
        # Nếu là thư mục, duyệt qua tất cả tệp tin trong thư mục
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                file_length = os.path.getsize(file_path)
                relative_path = os.path.relpath(file_path, path).split(os.sep)
                file_info.append({
                    'length': file_length,
                    'path': relative_path
                })
    else:
        # Nếu là tệp tin, chỉ cần thêm thông tin của nó
        file_length = os.path.getsize(path)
        relative_path = [os.path.basename(path)]
        file_info.append({
            'length': file_length,
            'path': relative_path
        })
    return file_info


def create_metainfo(path, announce_url='tracker', author = '123', comment = 'test-torrent'):
    """Tạo file metainfo cho torrent."""
    files = get_file_info(path)
    
    # Tính toán các thông số cần thiết
    piece_length = 524288  # 512 KB
    pieces = 'ABCXYZ'
    filename = os.path.basename(path)
    info_data = {
            "name": filename,
            "pieceLength": piece_length,
            "pieces": pieces,  # Chuyển đổi thành chuỗi hex
            "files": files
        }

    code = hashSHA1(info_data)

    metainfo = {
        "author": author,
        "hashCode": code,
        "announce": announce_url,
        "info": info_data,
        "creationDate": int(time.time()),  # Thời gian hiện tại
        "comment": comment,
    }

    return metainfo, filename


async def add(path):
    metainfo, filename = create_metainfo(path)
    response = await postAPI(f'{HOST}/metainfo', metainfo)
    if (response.get("status")): 
        print(f"Added  {metainfo.get("hashCode")}  {filename}")
    else: 
        print(f"\033[1;31m{response.get('message')}\033[0m")


async def delete(code): 
    data =  {
        "peerId" : "123", 
        "hashCode": code
    }
    response = await postAPI(f'{HOST}/delete', data)
    if (response.get("status")): 
        print(f"{response.get('message')}")
    else: 
        print(f"\033[1;31m{response.get('message')}\033[0m")


async def ls(peeerId): 
    response = await fetchAPI(f'{HOST}/list/123')
    if (response.get("status")): 
        # Định nghĩa chiều dài cố định cho mỗi cột
        file_name_width = 20
        hash_code_width = 45
        time_save_width = 30

        print(f"{'File Name'.ljust(file_name_width)} {'Hash Code'.ljust(hash_code_width)} {'Time Save'.ljust(time_save_width)}")
        print('-' * (file_name_width + hash_code_width + time_save_width))

        for data in response.get("repo"): 
            file_name = data.get("fileName")
            hash_code = data.get("hashCode")
            time_save = data.get("timeSave")
            
            print(f"{file_name.ljust(file_name_width)} {hash_code.ljust(hash_code_width)} {time_save.ljust(time_save_width)}")
    else: 
        print(f"\033[1;31m{response.get('message')}\033[0m")



async def main():
    # path = input(">> ")
    await ls(123)

if __name__ == '__main__': 
    asyncio.run(main())