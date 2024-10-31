
def display_progress(stdscr):
    """Hiển thị thông tin tiến độ tải xuống"""
    global running, downloading
    curses.curs_set(0)  # Ẩn con trỏ
    stdscr.clear()

    while running and downloading:
        stdscr.clear()
        stdscr.addstr("Current Download Status:\n")

        for file_name, status in torrent_status.items():
            progress_bar = "#" * (status["progress"] // 2) + "." * (50 - (status["progress"] // 2))
            stdscr.addstr(f"{file_name: <10}   download: {status['download']}kb   "
                          f"upload: {status['upload']}kgb"
                          f"[{status['progress']}%]   [{progress_bar}]\n")

        stdscr.addstr("\nPress E to exit\n")
        stdscr.refresh()
        
        # Kiểm tra xem phím được nhấn có phải là 'E' không
        if stdscr.getch() == ord('e'):
            downloading = False  # Dừng tải xuống
            break