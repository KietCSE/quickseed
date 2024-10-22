import os
import aiohttp
import asyncio 
from auth import login, register
from add_delete_ls import add, delete, ls

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
    arg = command.split()
    """Process the command entered by the user"""
    match arg[0]:
        case "add":
            await add(arg[1])
        case "delete":
            await delete(arg[1])
        case "ls": 
            await ls("123")
        case "help":
            show_help()
        case "clear":
            clear_screen()
        case _:
            print(f"Unrecognized command: {command}. Type 'help' for available commands.")


async def main():
    choice = input("Do you want to [1] Register or [2] Login? (exit to quit): ").strip()
    if choice == '1':
        if await register():
            while True:
                prompt = "\033[1;32m[Torrent]\033[0m \033[1;93m➜\033[0m "
                command = input(prompt).strip() 
                if command == 'exit': break
                if command: await process_command(command)
    elif choice == '2':
        if await login():
            while True:
                prompt = "\033[1;32m[Torrent]\033[0m \033[1;93m➜\033[0m "
                command = input(prompt).strip() 
                if command == 'exit': break
                if command: await process_command(command)
    elif choice.lower() == 'exit':
        print("Exiting the program.")
    else:
        print(text_color("Invalid choice. Please choose 1 or 2.", "red"))
    



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting program...")

