import fetch_api as api
from config import HOST
import getpass

def login():
    print("Login successful!")
    print(HOST)
    return True
    """Function to handle user login"""
    username = input("Username: ")
    password = getpass.getpass("Password: ")  # Sử dụng getpass để nhập mật khẩu mà không hiển thị
    # Kiểm tra tên người dùng và mật khẩu (giả định có tên và mật khẩu hợp lệ)
    

    if username == "admin" and password == "password123":
        print("Login successful!")
        return True
    else:
        print("Invalid username or password.")
        return False


login()