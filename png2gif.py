import os
import glob

def delete_png_files(folder_path):
    """Hàm phụ trợ: Xóa toàn bộ file .png trong thư mục được chỉ định"""
    search_pattern = os.path.join(folder_path, '*.png')
    png_files = glob.glob(search_pattern)
    
    count = 0
    for file in png_files:
        try:
            os.remove(file)
            count += 1
        except Exception as e:
            print(f"Lỗi: Không thể xóa {file} - {e}")
            
    return count

def run_app():
    while True:
        # ==========================================
        # MENU CẤP 1: CHỌN HÀNH ĐỘNG CHÍNH
        # ==========================================
        print("\n" + "="*50)
        print("CÔNG CỤ XỬ LÝ VIDEO VÀ ẢNH PNG")
        print("1. TẠO ẢNH PNG (Trích xuất từ video MP4)")
        print("2. XÓA ẢNH PNG (Dọn dẹp thư mục)")
        print("0. Thoát chương trình")
        print("="*50)
        
        main_choice = input("Nhập chức năng bạn muốn sử dụng (1/2/0): ").strip()
        
        if main_choice == '0' or main_choice.lower() == 'exit':
            print("Đang thoát chương trình...")
            break
            
        if main_choice not in ['1', '2']:
            print("Lựa chọn không hợp lệ, vui lòng nhập lại.")
            continue

        # ==========================================
        # MENU CẤP 2: CHỌN QUY MÔ XỬ LÝ
        # ==========================================
        print("\n" + "-"*40)
        print("CHỌN CHẾ ĐỘ THỰC THI:")
        print("1. Thủ công (Chỉ định 1 Book và 1 Thư mục con)")
        print("2. Tự động (Quét toàn bộ thư mục con trong 1 Book)")
        print("0. Quay lại Menu chính")
        print("-"*40)
        
        sub_choice = input("Nhập chế độ (1/2/0): ").strip()
        
        if sub_choice == '0' or sub_choice.lower() == 'exit':
            continue # Quay lại vòng lặp chính (Menu cấp 1)

        # ---------------------------------------------------------
        # KHỐI LOGIC 1: CHỨC NĂNG TẠO ẢNH PNG (MAIN = 1)
        # ---------------------------------------------------------
        if main_choice == '1':
            
            # [TẠO - THỦ CÔNG]
            if sub_choice == '1':
                input_pathA = input("Nhập đường dẫn đến thư mục sách: ").strip()
                if input_pathA.lower() == 'exit': continue

                input_pathB = input("Nhập đường dẫn đến tệp/thư mục con: ").strip()
                if input_pathB.lower() == 'exit': continue
                
                book = os.path.splitext(os.path.basename(input_pathA))[0]
                directory = os.path.splitext(os.path.basename(input_pathB))[0]
                filename = directory

                target_dir = f"D:\\holoAnime_LaTeX\\Image\\Book{book}\\{directory}"
                cmd = f'cd /d "{target_dir}" && ffmpeg -i {filename}.mp4 -vf fps=30 {filename}.%01d.png'
                
                print(f"\nLệnh chuẩn bị chạy:\n{cmd}")
                if input("Xác nhận chạy lệnh? (y/n): ").strip().lower() == 'y':
                    os.system(cmd)
                    print(f"-> Đã tạo PNG xong cho {directory}.")

            # [TẠO - TỰ ĐỘNG]
            elif sub_choice == '2':
                input_pathA = input("Nhập đường dẫn đến thư mục sách cần quét: ").strip()
                if input_pathA.lower() == 'exit': continue
                
                book = os.path.splitext(os.path.basename(input_pathA))[0]
                base_dir = f"D:\\holoAnime_LaTeX\\Image\\Book{book}"
                
                if not os.path.exists(base_dir):
                    print(f"Lỗi: Không tìm thấy {base_dir}")
                    continue
                    
                commands = []
                for item in os.listdir(base_dir):
                    item_path = os.path.join(base_dir, item)
                    if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, f"{item}.mp4")):
                        cmd = f'cd /d "{item_path}" && ffmpeg -i {item}.mp4 -vf fps=60 {item}.%01d.png'
                        commands.append((item, cmd))
                
                if not commands:
                    print("Không tìm thấy file MP4 nào hợp lệ để trích xuất.")
                    continue
                    
                print(f"\nTìm thấy {len(commands)} tệp MP4 cần xử lý.")
                if input("Bắt đầu trích xuất hàng loạt? (y/n): ").strip().lower() == 'y':
                    for i, (folder_name, cmd) in enumerate(commands, 1):
                        print(f"\n[{i}/{len(commands)}] Đang trích xuất: {folder_name}...")
                        os.system(cmd)
                    print("\n-> ĐÃ HOÀN TẤT TẠO ẢNH HÀNG LOẠT!")

        # ---------------------------------------------------------
        # KHỐI LOGIC 2: CHỨC NĂNG XÓA ẢNH PNG (MAIN = 2)
        # ---------------------------------------------------------
        elif main_choice == '2':
            
            # [XÓA - THỦ CÔNG]
            if sub_choice == '1':
                input_pathA = input("Nhập đường dẫn đến thư mục sách: ").strip()
                if input_pathA.lower() == 'exit': continue

                input_pathB = input("Nhập đường dẫn đến tệp/thư mục con: ").strip()
                if input_pathB.lower() == 'exit': continue
                
                book = os.path.splitext(os.path.basename(input_pathA))[0]
                directory = os.path.splitext(os.path.basename(input_pathB))[0]
                
                target_dir = f"D:\\holoAnime_LaTeX\\Image\\Book{book}\\{directory}"
                
                if not os.path.exists(target_dir):
                    print("Lỗi: Thư mục không tồn tại!")
                    continue
                    
                print(f"\nCẢNH BÁO: Bạn sắp xóa toàn bộ file PNG trong thư mục {target_dir}")
                if input("Xác nhận xóa? (y/n): ").strip().lower() == 'y':
                    deleted = delete_png_files(target_dir)
                    print(f"-> Đã dọn dẹp {deleted} file PNG.")

            # [XÓA - TỰ ĐỘNG]
            elif sub_choice == '2':
                input_pathA = input("Nhập đường dẫn đến thư mục sách cần quét dọn: ").strip()
                if input_pathA.lower() == 'exit': continue
                
                book = os.path.splitext(os.path.basename(input_pathA))[0]
                base_dir = f"D:\\holoAnime_LaTeX\\Image\\Book{book}"
                
                if not os.path.exists(base_dir):
                    print(f"Lỗi: Không tìm thấy {base_dir}")
                    continue
                
                # Tìm các thư mục con có khả năng chứa PNG
                folders_to_clean = [os.path.join(base_dir, f) for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
                
                print(f"\nSẽ tiến hành quét và dọn dẹp PNG trong {len(folders_to_clean)} thư mục con thuộc Book{book}.")
                if input("Bạn có chắc chắn muốn DỌN DẸP HÀNG LOẠT không? (y/n): ").strip().lower() == 'y':
                    total_deleted = 0
                    for folder_path in folders_to_clean:
                        deleted = delete_png_files(folder_path)
                        if deleted > 0:
                            print(f"- Xóa {deleted} ảnh tại: {os.path.basename(folder_path)}")
                            total_deleted += deleted
                            
                    print(f"\n-> HOÀN TẤT! Tổng cộng đã xóa {total_deleted} file PNG trong Book{book}.")

if __name__ == "__main__":
    try:
        run_app()
    except Exception as e:
        print(f"Đã xảy ra lỗi hệ thống: {e}")
    finally:
        input("\nNhấn Enter để thoát chương trình.")