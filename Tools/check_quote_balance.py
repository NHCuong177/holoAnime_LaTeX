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

    # Stack chứa các phần tử ('D', dòng, cột) cho ngoặc kép `` đang mở,
    # hoặc ('S', dòng, cột) cho ngoặc đơn lồng bên trong (dấu ` lẻ) đang mở
    stack = []
    issues = []

    for line_num, line in enumerate(lines, 1):
        # 1. BỎ QUA COMMENT: Dùng Regex xóa mọi thứ từ dấu % (không bị escape bằng \) đến cuối dòng
        clean_line = re.sub(r'(?<!\\)%.*', '', line)

        # 2. XỬ LÝ BẰNG STACK: Quét qua file, gom từng cụm dấu ` hoặc ' liên tiếp
        #    - `` (hoặc nhiều hơn) => mở ngoặc kép
        #    - `  (1 dấu)         => mở ngoặc đơn LỒNG bên trong (vd: `Câu lạc bộ...')
        #    - '' (hoặc nhiều hơn) => đóng ngoặc kép
        #    - '  (1 dấu)         => đóng ngoặc đơn lồng, HOẶC dấu nháy đơn/sở hữu cách tiếng Anh (Louis', don't)
        for match in re.finditer(r"`+|'+", clean_line):
            token = match.group()
            col = match.start()

            if token[0] == '`':
                if len(token) >= 2:
                    # Mở ngoặc kép ``
                    stack.append(('D', line_num, col))
                    # Nếu dư ra hơn 2 dấu ` (vd ```), coi phần dư là các dấu mở ngoặc đơn lồng kế tiếp
                    for _ in range(len(token) - 2):
                        stack.append(('S', line_num, col))
                else:
                    # Mở ngoặc đơn lồng bên trong ngoặc kép
                    stack.append(('S', line_num, col))
            else:
                if len(token) >= 2:
                    # Đóng ngoặc kép ''
                    # Trước tiên, đóng (báo thiếu) các ngoặc đơn lồng chưa được đóng còn kẹt trên đỉnh Stack
                    while stack and stack[-1][0] == 'S':
                        open_s = stack.pop()
                        issues.append((open_s[1], f"Thiếu dấu đóng (') cho ngoặc đơn lồng (`) mở tại cột {open_s[2]}"))
                    if stack and stack[-1][0] == 'D':
                        stack.pop()
                    else:
                        issues.append((line_num, f"Dư dấu đóng ngoặc kép ('') tại cột {col} (Không có dấu mở tương ứng)"))
                else:
                    # Chỉ có 1 dấu ' duy nhất
                    prev_char = clean_line[col - 1] if col > 0 else ''

                    if stack and stack[-1][0] == 'S':
                        # Ưu tiên coi đây là đóng ngoặc đơn LỒNG hợp lệ, vd:
                        # ``...`Câu lạc bộ Lục lạc'...''
                        stack.pop()
                    elif prev_char.isalpha():
                        # Sở hữu cách / rút gọn tiếng Anh: Louis', Rei's, don't, isn't...
                        # -> Không phải lỗi, bỏ qua
                        pass
                    else:
                        issues.append((line_num, f"Cảnh báo: Dấu nháy đơn (') lẻ loi tại cột {col} (Có thể lỗi chính tả)"))

    # 3. KIỂM TRA STACK CUỐI FILE: Những gì còn kẹt lại chính là các dấu mở chưa được đóng!
    for kind, ln, col in stack:
        if kind == 'D':
            issues.append((ln, f"Thiếu dấu đóng ngoặc kép ('') cho dấu mở (``) tại cột {col}"))
        else:
            issues.append((ln, f"Thiếu dấu đóng (') cho ngoặc đơn lồng (`) mở tại cột {col}"))

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