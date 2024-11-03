import os
import aiohttp
import asyncio 
import signal
import threading
from auth import login, register
from add_delete_ls import add, delete, ls
from get_seed_peers import get, seed
from scrape import scrape
import state as var
import sys
import ctypes

def text_color(command, color): 
    match color: 
        case 'blue': return f"\033[1;34m{command}\033[0m"
        case 'red' : return f"\033[1;31m{command}\033[0m"
        case 'green': return f"\033[1;32m{command}\033[0m"
        case 'purple': return f"\033[1;35m{command}\033[0m"


def show_help():
    """Display usage instructions and available commands"""
    help_text = """
    Available commands:
    -------------------------
    add             - Publish your documents into network
    delete  <code>  - Delete your published documents
    ls              - List all your published documents 
    seed    <code>  - Start sharing your documents 
    get     <code>  - Start downloading documents
    stop    <code>  - Stop downloading/sharing documents 
    show            - Show all progress of download
    peers   <code>  - List all peers you are connecting 
    scrape  <code>  - Check currrent infomation of torrent network
    help            - Display available commands
    clear           - Clear the screen
    logout          - Log out your account 
    exit            - Exit the program
    """
    print(help_text)


def clear_screen():
    """Clear the terminal screen based on the operating system"""
    os.system('cls' if os.name == 'nt' else 'clear')


async def process_command(command):
    args = command.split()
    """Process the command entered by the user"""
    match args[0]:
        case "add":
            await add(args[1])
        case "delete":
            await delete(args[1])
        case "ls": 
            await ls(var.PEER_ID)
        case "get": 
            from get_seed_peers import get
            await get(args[1])
        case "seed": 
            await seed(args[1])
        case "help":
            show_help()
        case "clear":
            clear_screen()
        case "scrape":
            await scrape(args[1])
        case _:
            print(f"Unrecognized command: {command}. Type 'help' for available commands.")


async def main():
    choice = input("Do you want to [1] Register or [2] Login? (exit to quit): ").strip()
    if choice == '1':
        if await register():
            while True:
                prompt = "\033[1;32m[Torrent]\033[0m \033[1;93m➜\033[0m "
                command = input(prompt).strip() 
                if command == 'exit': self_kill()
                if command == 'logout': await main() 
                if command: await process_command(command)
    elif choice == '2':
        if await login():
            while True:
                prompt = "\033[1;32m[Torrent]\033[0m \033[1;93m➜\033[0m "
                command = input(prompt).strip() 
                # stop current process
                if command == 'exit': self_kill()   
                if command == 'logout': await main() 
                if command: await process_command(command)
    elif choice.lower() == 'exit':
        print("Exiting the program.")
    else:
        print(text_color("Invalid choice. Please choose 1 or 2.", "red"))


# def self_kill():
<<<<<<< HEAD
    # os.kill(os.getpid(), signal.SIGKILL)
=======
#     os.kill(os.getpid(), signal.SIGKILL)

>>>>>>> 5a2a041198e50b7dcf2c5df5757e11eae7fcb06f
def self_kill():
    if os.name == 'nt':  # Kiểm tra nếu chạy trên Windows
        # Lấy ID của tiến trình hiện tại
        pid = os.getpid()
        # Mở tiến trình hiện tại với quyền để kết thúc
        handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
        # Kết thúc tiến trình
        ctypes.windll.kernel32.TerminateProcess(handle, -1)
    else:
        # Trên Unix-based (như Linux, macOS), dùng SIGKILL
        os.kill(os.getpid(), signal.SIGKILL)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting program...")
        pass

