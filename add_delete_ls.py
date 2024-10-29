import os
import time
import json
import hashlib
from fetch_api import *
from config import HOST, BENCODE
import bencodepy
# import bencodepy

def hashSHA1(data):
    """Hash một đối tượng Python bằng thuật toán SHA-1."""
    # Kiểm tra xem dữ liệu có phải là kiểu bytes hay không
    if not isinstance(data, bytes):
        # Nếu không phải là bytes, kiểm tra kiểu dữ liệu
        if isinstance(data, str):
            # Nếu là chuỗi, mã hóa thành bytes
            data = data.encode('utf-8')
        else:
            # Nếu là một đối tượng khác, chuyển đổi thành chuỗi JSON và mã hóa
            data = json.dumps(data, sort_keys=True).encode('utf-8')
    
    # Tạo hash SHA-1
    sha1_hash = hashlib.sha1(data).hexdigest()  # Chuyển đổi sang chuỗi hex
    return sha1_hash


def get_file_info(path):
    file_info = []
    pieces=''
    leftover_data = b''

    def process_file(file_path):
        nonlocal leftover_data
        nonlocal pieces
        # pieces = []
        
        file_length = os.path.getsize(file_path)
        relative_path = os.path.relpath(file_path, path).split(os.sep)

        with open(file_path, 'rb') as f:
            while True:
                chunk = leftover_data + f.read(10 - len(leftover_data))
                # print(chunk)
                if not chunk: break

                if len(chunk) == 10:
                    piece_hash = hashSHA1(chunk)
                    pieces += piece_hash
                    leftover_data = b''  # Reset leftover data as it's fully used
                else:
                    # If it's less than 512 KB, keep it in leftover_data for the next file
                    leftover_data = chunk
                    break  # Stop reading and move to the next file to complete this leftover

        file_info.append({
            'length': file_length,
            'path': relative_path,
        })


    if os.path.isdir(path):
        # Nếu là thư mục, duyệt qua tất cả tệp tin trong thư mục
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                process_file(file_path)
    else:
        # Nếu là tệp tin, chỉ cần thêm thông tin của nó
        process_file(file_path)
    
    
    pieces += hashSHA1(leftover_data)
    # print(pieces)

    result = [pieces[i:i + 40] for i in range(0, len(pieces), 40)]
    # print(result)

    return file_info, pieces


def create_metainfo(path, announce_url='tracker', author = '123', comment = 'test-torrent'):
    """Tạo file metainfo cho torrent."""
    files, pieces = get_file_info(path)
    
    # Tính toán các thông số cần thiết
    piece_length = 524288  # 512 KB
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
    # print (metainfo)
    return metainfo, filename


async def add(path):
    metainfo, filename = create_metainfo(path)   #can them du lieu o doan nay  

    # if BENCODE: 
    #     metainfo = bencodepy.encode(metainfo)

    response = await postAPI(f'{HOST}/metainfo', metainfo)
    print(response)
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


async def ls(peerId): 
    response = await fetchAPI(f'{HOST}/list/{peerId}')
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
    result = create_metainfo('test')
    bencoded_data = bencodepy.encode(result)
    print(type(bencoded_data))
    decoded_data = decode_bencoded(bencoded_data)
    print(type(decoded_data))
    # print(file_info)

if __name__ == '__main__': 
    asyncio.run(main())