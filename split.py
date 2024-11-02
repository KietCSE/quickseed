import os
import time
import math
from bitarray import bitarray
import hashlib
from get_seed_peers import Metainfo

PIECE_SIZE = 1024*128

SPLIT_CHAR = '---'

BIT_ARRAY = None

def create_or_load_bitarray(filename):
    directory = 'current_state'
    file_path = os.path.join(directory, filename)
    
    # Kiểm tra nếu file đã tồn tại
    if os.path.exists(file_path):
        # Tải bitarray từ file
        print("Đang tải bitarray từ tệp hiện có...")
        with open(file_path, 'r') as f:
            binary_string = f.read()  # Đọc dữ liệu nhị phân từ tệp
        # Chuyển đổi chuỗi nhị phân thành bitarray
        list_downloaded_piece = bitarray(binary_string)
        BIT_ARRAY = list_downloaded_piece
        return list_downloaded_piece

    else:
        # Tạo bitarray mới nếu file chưa tồn tại
        print("Tạo mới bitarray và lưu vào tệp...")
        num_piece = 0
        files = Metainfo["info"]["files"]

        for e in files: 
            num_piece += math.ceil(e["length"] / PIECE_SIZE)

        # Tạo bitarray với số lượng miếng
        list_downloaded_piece = bitarray(num_piece)
        list_downloaded_piece.setall(0)  # Đặt tất cả các bit thành 0 (chưa tải)

        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(directory, exist_ok=True)
        
        # Lưu bitarray vào tệp
        with open(file_path, 'w') as f:
            f.write(list_downloaded_piece.to01())  # Lưu dưới dạng chuỗi nhị phân

        BIT_ARRAY = list_downloaded_piece
        return list_downloaded_piece



# # Đọc dữ liệu từ tệp và tải vào bitarray
# def load_bitarray_from_file(file_path):
#     # Đọc chuỗi nhị phân từ tệp
#     with open(file_path, 'r') as f:
#         binary_string = f.read()  # Đọc dữ liệu nhị phân từ tệp
#     # Chuyển đổi chuỗi nhị phân thành bitarray
#     loaded_bitarray = bitarray(binary_string)
#     return loaded_bitarray


def save_bitarray(bitarray, filename): 
    # Đường dẫn tệp
    directory = 'current_state'
    file_path = os.path.join(directory, filename)
    
    # Tạo thư mục nếu chưa tồn tại
    os.makedirs(directory, exist_ok=True)
    try: 
        # Lưu bitarray vào tệp
        with open(file_path, 'w') as f:
            f.write(bitarray.to01())  # Lưu dưới dạng chuỗi nhị phân
        return True
    except Exception as e: 
        return False


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



def split_file(index, file_path, output_dir, piece_size=PIECE_SIZE):
    # Kiểm tra xem thư mục đầu ra có tồn tại không, nếu không thì tạo
    os.makedirs(output_dir, exist_ok=True)
    # Mở file để đọc
    with open(file_path, 'rb') as file:
        while True:
            # Đọc một phần từ file
            piece = file.read(piece_size)
            if not piece:  # Nếu không còn dữ liệu để đọc, thoát khỏi vòng lặp
                break
            
            # Tạo tên file cho piece
            piece_filename = os.path.join(output_dir, f'piece_{index}.bin')
            index += 1

            # Lưu piece vào file
            with open(piece_filename, 'wb') as piece_file:
                piece_file.write(piece)
            hashcode = hashSHA1(piece)

    print(f'File đã được chia và lưu vào thư mục "{output_dir}".')
    return index, hashcode


def merge_files(input_dir, target_file):
    target_dir = os.path.dirname(target_file)  # Lấy đường dẫn thư mục của target_file
    os.makedirs(target_dir, exist_ok=True) 

    # Lấy danh sách các file piece và sắp xếp theo thứ tự tên
    piece_files = sorted(
        [f for f in os.listdir(input_dir) if f.startswith('piece_')],
        key=lambda x: int(x.split('_')[1].split('.')[0])  # Sắp xếp theo số thứ tự
    )
    
    # Mở file để ghi
    with open(target_file, 'wb') as target:
        for piece in piece_files:
            piece_path = os.path.join(input_dir, piece)
            with open(piece_path, 'rb') as piece_file:
                target.write(piece_file.read())  # Ghi nội dung của mỗi piece vào file hoàn chỉnh
    print(f'File đã được ghép lại và lưu tại "{target_file}".')



#dir: creationDate 
#filename in metainfo
def merge(dir, filename):
    is_exit = os.path.isdir('target/' + filename)
    if (is_exit): 
        print("Exit folder with the same name!!")
        return 

    for root, dirs, files in os.walk(dir):
        for folder in dirs:
            input_dir = os.path.join(root, folder)
            # Đặt tên file đích cho mỗi thư mục, chẳng hạn dựa trên tên thư mục
            current_folder_name = os.path.basename(input_dir)
            target_file = "target/" + current_folder_name.replace(SPLIT_CHAR, '/')
            # Gọi hàm merge_files cho thư mục con
            merge_files(input_dir, target_file)



#split file and store in dict
def get_file_info(path):
    file_info = []
    creationDate = int(time.time())
    file_name = os.path.basename(path)
    index = 0
    pieces = ''

    if os.path.isdir(path):
        # Nếu là thư mục, duyệt qua tất cả tệp tin trong thư mục
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                file_length = os.path.getsize(file_path) 
                relative_path = os.path.relpath(file_path, path)
                relative_path_array = relative_path.split(os.sep)
                output_dir = file_name + SPLIT_CHAR + relative_path.replace("/", SPLIT_CHAR)
                index, code = split_file(index, file_path, f'dict/{creationDate}/{output_dir}')
                pieces += code
                file_info.append({
                    'length': file_length,
                    'path': relative_path_array
                })
    else:
        # Nếu là tệp tin, chỉ cần thêm thông tin của nó
        file_length = os.path.getsize(path)
        relative_path = [os.path.basename(path)]
        output_dir = file_name + SPLIT_CHAR + os.path.basename(path)
        index, code = split_file(index, path, f'dict/{creationDate}/{output_dir}')
        pieces += code

        file_info.append({
            'length': file_length,
            'path': relative_path
        })

    return file_info , creationDate, pieces



# Metainfo = {
#     "info":{
#         "name" : "chrome",
#         "files": [{'length': 11207, 'path': ['popup.css']}, {'length': 5167527, 'path': ['4.1_video_slides.pptx']}, {'length': 440, 'path': ['manifest.json']}, {'length': 2731, 'path': ['icon-with-shadow.svg']}, {'length': 965300, 'path': ['91d29ff3905f37016e4e.jpg']}, {'length': 22987, 'path': ['icon', 'icon.png']}, {'length': 2941, 'path': ['icon', '48.png']}, {'length': 1630, 'path': ['icon', '32.png']}, {'length': 12669, 'path': ['icon', '128.png']}, {'length': 8080, 'path': ['icon', '96.png']}, {'length': 698, 'path': ['icon', '16.png']}, {'length': 12019, 'path': ['src', 'content', 'content.js']}, {'length': 23934, 'path': ['src', 'background', 'background.js']}, {'length': 369907, 'path': ['src', 'popup', 'popup.js']}, {'length': 734, 'path': ['src', 'popup', 'popup.html']}]
#     }, 
#     "creationDate":  1730521292
# }


def save_piece(data, index, creationDate):
    files =  Metainfo["info"]["files"]
    count_piece = -1
    is_save = False

    for piece in files:
        max_piece = math.ceil(piece["length"] / PIECE_SIZE)
        count_piece += max_piece
        # print("xet trong ", count_piece)
        try: 
            if (index <= count_piece): 
                relative_path = SPLIT_CHAR.join(piece["path"])
                path_file = f'dict/{creationDate}/{Metainfo["info"]["name"]}{SPLIT_CHAR}{relative_path}'

                os.makedirs(path_file, exist_ok=True)

                if os.path.exists(os.path.dirname(path_file)):
                    print(f"Thư mục đã được tạo thành công: {os.path.dirname(path_file)}")
                else:
                    print(f"Không thể tạo thư mục: {os.path.dirname(path_file)}")

                #luu piece 
                piece_filename = os.path.join(path_file, f'piece_{index}.bin')
                # Lưu piece vào file
                with open(piece_filename, 'wb') as piece_file:
                    piece_file.write(data)
                    is_save = True
                    break
        except Exception as e:  # Sửa lại cách xử lý ngoại lệ
            print(f"Lỗi khi lưu piece: {e}")

    if not is_save: print("khong luu duoc piece")



def get_piece(index, creationDate):
    files =  Metainfo["info"]["files"]
    count_piece = -1

    for piece in files:
        max_piece = math.ceil(piece["length"] / PIECE_SIZE)
        count_piece += max_piece
        # print("xet trong ", count_piece)

        if (index <= count_piece): 
            relative_path = SPLIT_CHAR.join(piece["path"])
            path_file = f'dict/{creationDate}/{Metainfo["info"]["name"]}{SPLIT_CHAR}{relative_path}/piece_{index}.bin'
        
        # Open the file and read the data inside
            try:
                with open(path_file, 'rb') as file:
                    data = file.read()  # Read the binary data from the piece file
                    return data  # Return the read data
            except FileNotFoundError:
                print(f"File not found: {path_file}")
                return None  # Return None if the file does not exist
    return None



def main(): 
    # Sử dụng hàm
    # file_location = '241_BTL_CD1.pdf'  # Đường dẫn đến file bạn muốn chia tách
    # output_directory = 'dict'  # Đường dẫn đến thư mục lưu các piece
    # # split_file(file_location, output_directory)
    # merge_files(output_directory, 'target')
    # print(get_file_info('/home/tuankiet/Documents/chrome'))

    merge('dict/1730530735', 'chrome')
    # print(load_bitarray_from_file("current_state/list1.txt"))
    # data = get_piece(100, 1730426447)
    # save(data, 100, 1730427319)
#     create_bitarray()
#     file_path = "current_state/list1.txt"
#     loaded_bitarray = load_bitarray_from_file(file_path)
#     print("Loaded bitarray:", loaded_bitarray)  # In ra bitarray đã tải lại
    
#     # Kiểm tra độ dài của bitarray
#     bitarray_length = len(loaded_bitarray)  # Số lượng bit trong bitarray
#     print("Length of bitarray (in bits):", bitarray_length)

#    # Chuyển đổi bitarray thành bytes và lấy kích thước
#     bitarray_as_bytes = loaded_bitarray.tobytes()  # Chuyển đổi sang bytes
#     bitarray_size_in_bytes = len(bitarray_as_bytes)  # Kích thước trong byte
#     # bitarray_size_in_bits = bitarray_size_in_bytes * 8  # Chuyển đổi sang bit
#     print("Size of bitarray (in bits):", bitarray_size_in_bytes)

if __name__ == '__main__': 
    main()


