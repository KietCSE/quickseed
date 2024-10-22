from fetch_api import *
from config import HOST
import getpass
import state as var

async def login():
    while True: 
        username = input("Username: ")
        password = getpass.getpass("Password: ")  # Sử dụng getpass để nhập mật khẩu mà không hiển thị
        
        data = {
            "account": username, 
            "password": password
        }

        response = await postAPI(f'{HOST}/login', data)
        if (response.get("status")): 
            print("Login successfully!")
            var.PEER_ID = response.get("peerId")
            return True
        else: 
            print(f"\033[1;31m{response.get('message')}\033[0m")


async def register(): 
    while True: 
        username = input("Username: ")
        password = getpass.getpass("Password: ")  # Sử dụng getpass để nhập mật khẩu mà không hiển thị
        confirm = getpass.getpass("Confirm password: ")  # Sử dụng getpass để nhập mật khẩu mà không hiển thị
        
        if password != confirm: 
            print(f"\033[1;31mIncorrect confirmed password\033[0m")
            continue

        data = {
            "account" : username, 
            "password": password
        }

        response = await postAPI(f'{HOST}/register', data)
        if (response.get("status")): 
            print("Register successfully!")
            PEER_ID = response.get("peerId")
            return True
        else: 
            print(f"\033[1;31m{response.get('message')}\033[0m")



async def main():
    await register()
    

if __name__ == "__main__":
    asyncio.run(main())



    