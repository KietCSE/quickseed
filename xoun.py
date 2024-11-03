def save_numbers_to_file(filename):
    # Tạo danh sách số từ 0 đến 6453
    numbers = list(range(94))  # 6454 vì range không bao gồm số cuối cùng
    
    # Chuyển đổi danh sách thành chuỗi theo định dạng yêu cầu
    numbers_str = "[" + ", ".join(map(str, numbers)) + "]"
    
    # Mở tệp và ghi vào đó
    with open(filename, 'w') as file:
        file.write(numbers_str)

# Sử dụng hàm để lưu vào tệp
save_numbers_to_file('status.txt')
