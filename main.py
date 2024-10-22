import os


def text_color(command, color): 
    match color: 
        case 'blue': return f"\033[1;34m{command}\033[0m"
        case 'red' : return f"\033[1;31m{command}\033[0m"
        case 'green': return f"\033[1;32m{command}\033[0m"
        case 'purple': return f"\033[1;35m{command}\033[0m"


def show_help():
    """Display usage instructions and available commands"""
    help_text = f"""
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

def login():
    print("Login successful!")
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


def register():
    print("Register successfully")
    return True


def process_command(command):
    """Process the command entered by the user"""
    match command:
        case "start":
            print("Starting torrent download...")
        case "stop":
            print("Stopping torrent download...")
        case "help":
            show_help()
        case "clear":
            clear_screen()
        case _:
            print(f"Unrecognized command: {command}. Type 'help' for available commands.")


def main():
    try:
        choice = input("Do you want to [1] Register or [2] Login? (exit to quit): ").strip()
        if choice == '1':
            if register():
                try:
                    while True:
                        prompt = "\033[1;32m[Torrent]\033[0m \033[1;93m➜\033[0m "
                        command = input(prompt).strip() 
                        if command == 'exit': break
                        if command: process_command(command)
                except KeyboardInterrupt:
                    print("\nStop program")    
        
        elif choice == '2':
            if login():  # Kiểm tra xem đăng nhập có thành công hay không
                try:
                    while True:
                        prompt = "\033[1;32m[Torrent]\033[0m \033[1;93m➜\033[0m "
                        command = input(prompt).strip() 
                        if command == 'exit': break
                        if command: process_command(command)      
                except KeyboardInterrupt:
                    print("\nStop program")

        
        elif choice.lower() == 'exit':
            print("Exiting the program.")
        else:
            print(text_color("Invalid choice. Please choose 1 or 2.", "red"))
    
    except KeyboardInterrupt:
        print("\nStop program")



if __name__ == "__main__":
    main()
