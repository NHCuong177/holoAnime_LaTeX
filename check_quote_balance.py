import os
import re

def check_file(file_path):
    print(f"\n[{os.path.basename(file_path)}] Đang kiểm tra...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"  [!] Lỗi khi đọc file: {e}")
        return False

    stack = []
    issues = []

    for line_num, line in enumerate(lines, 1):
        # 1. BỎ QUA COMMENT: Dùng Regex xóa mọi thứ từ dấu % (không bị escape bằng \) đến cuối dòng
        clean_line = re.sub(r'(?<!\\)%.*', '', line)

        # 2. XỬ LÝ BẰNG STACK: Quét qua file tìm `` và '' theo đúng thứ tự
        for match in re.finditer(r"``|''", clean_line):
            token = match.group()
            col = match.start()
            
            if token == "``":
                # Đưa dấu mở vào Stack (lưu lại dòng và cột để báo cáo nếu quên đóng)
                stack.append((line_num, col))
            elif token == "''":
                if stack:
                    # Nếu có dấu mở trong Stack, lấy ra (Bắt cặp thành công)
                    stack.pop() 
                else:
                    # Nếu Stack rỗng mà lại có dấu đóng -> Bị dư dấu đóng
                    issues.append((line_num, f"Dư dấu đóng ngoặc (\\'\\') tại cột {col} (Không có dấu mở tương ứng)"))

        # 3. HEURISTIC: Kiểm tra dấu nháy đơn lẻ (Dựa trên clean_line để tránh comment)
        single_quotes = [m.start() for m in re.finditer(r"'", clean_line)]
        for idx in single_quotes:
            # Bỏ qua nếu là một phần của '' hoặc ``
            if (idx > 0 and clean_line[idx-1] == "'") or (idx < len(clean_line)-1 and clean_line[idx+1] == "'"):
                continue
            
            is_apostrophe = False
            if idx > 0 and clean_line[idx-1].isalpha():
                if idx < len(clean_line)-1 and clean_line[idx+1].isalpha():
                    is_apostrophe = True
                    
            if not is_apostrophe:
                issues.append((line_num, f"Cảnh báo: Dấu nháy đơn (') lẻ loi tại cột {idx} (Có thể lỗi chính tả)"))

    # 4. KIỂM TRA STACK CUỐI FILE: Những gì còn kẹt lại trong Stack chính là dấu `` chưa được đóng!
    for open_quote in stack:
        issues.append((open_quote[0], f"Thiếu dấu đóng ngoặc (\\'\\') cho dấu mở (``) tại cột {open_quote[1]}"))

    # Sắp xếp lại danh sách lỗi theo thứ tự dòng từ trên xuống dưới
    issues.sort(key=lambda x: x[0])

    # 5. IN KẾT QUẢ
    if not issues:
        print("  [OK] Tất cả dấu ngoặc kép đều cân bằng tuyệt đối!")
        return True
    else:
        print(f"  [X] Phát hiện {len(issues)} vấn đề:")
        for line_num, msg in issues[:15]:  # Giới hạn in ra 15 lỗi để đỡ trôi màn hình
            print(f"    - Dòng {line_num}: {msg}")
        if len(issues) > 15:
            print(f"    ... và {len(issues) - 15} vấn đề khác.")
        return False

def run_app():
    while True:
        # ==========================================
        # MENU TƯƠNG TÁC
        # ==========================================
        print("\n" + "="*50)
        print("CÔNG CỤ KIỂM TRA LỖI DẤU NGOẶC KÉP LATEX")
        print("1. Chế độ Thủ công (Kiểm tra 1 file .tex cụ thể)")
        print("2. Chế độ Tự động (Quét toàn bộ thư mục)")
        print("0. Thoát chương trình")
        print("="*50)
        
        main_choice = input("Nhập chức năng bạn muốn sử dụng (1/2/0): ").strip()
        
        if main_choice == '0' or main_choice.lower() == 'exit':
            print("Đang thoát chương trình...")
            break
            
        if main_choice not in ['1', '2']:
            print("Lựa chọn không hợp lệ, vui lòng nhập lại.")
            continue

        # ---------------------------------------------------------
        # KHỐI LOGIC 1: KIỂM TRA 1 FILE
        # ---------------------------------------------------------
        if main_choice == '1':
            path = input("\nNhập đường dẫn đến file (.tex): ").strip()
            if path.lower() == 'exit': continue
            
            # Xóa dấu nháy kép bọc ngoài do tính năng Copy as Path của Windows
            path = path.strip('"\'') 
            
            if os.path.isfile(path) and path.endswith('.tex'):
                check_file(path)
            else:
                print("Lỗi: File không tồn tại hoặc không phải là định dạng .tex!")

        # ---------------------------------------------------------
        # KHỐI LOGIC 2: QUÉT TOÀN BỘ THƯ MỤC
        # ---------------------------------------------------------
        elif main_choice == '2':
            dir_path = input("\nNhập đường dẫn đến thư mục cần quét: ").strip()
            if dir_path.lower() == 'exit': continue
            
            dir_path = dir_path.strip('"\'')
            
            if os.path.isdir(dir_path):
                found_files = []
                # Duyệt đệ quy toàn bộ thư mục con
                for root, _, files in os.walk(dir_path):
                    for file in files:
                        if file.endswith('.tex'):
                            found_files.append(os.path.join(root, file))
                            
                if not found_files:
                    print(f"Không tìm thấy file .tex nào trong: {dir_path}")
                else:
                    print(f"\nSẽ tiến hành quét {len(found_files)} file .tex.")
                    if input("Bạn có chắc chắn muốn bắt đầu quét? (y/n): ").strip().lower() == 'y':
                        error_count = 0
                        for f in found_files:
                            is_ok = check_file(f)
                            if not is_ok:
                                error_count += 1
                        print(f"\n-> HOÀN TẤT! Có {error_count}/{len(found_files)} file phát hiện lỗi.")
            else:
                print("Lỗi: Thư mục không tồn tại!")

if __name__ == "__main__":
    try:
        run_app()
    except Exception as e:
        print(f"Đã xảy ra lỗi hệ thống: {e}")
    finally:
        input("\nNhấn Enter để thoát chương trình.")