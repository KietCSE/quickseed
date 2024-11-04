import os
from dotenv import load_dotenv

# Tải biến môi trường
load_dotenv()

# Lấy các giá trị từ biến môi trường
HOST = os.getenv('HOST')
TEST = True
# TEST = int(os.getenv('TEST'))

BENCODE = True