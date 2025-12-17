# run_generator.py (Tên cũ là main.py)
import config
import generator
import os
import time
import shutil

def main():
    print(">>> Đang khởi tạo quá trình sinh dữ liệu...")
    start_time = time.time()
    
    # 1. Dọn dẹp folder cũ để tránh dữ liệu rác
    if os.path.exists("output_data"):
        shutil.rmtree("output_data") # Xóa sạch thư mục cũ
    os.makedirs("output_data")

    # 2. Sinh Topology
    topo_df, node_list = generator.generate_topology()
    topo_file = "output_data/network_topology.csv"
    topo_df.to_csv(topo_file, index=False, encoding='utf-8')
    print(f"✅ Đã tạo file Topology: {topo_file}")

    # 3. Sinh Traffic Logs
    traffic_df = generator.generate_traffic_data(node_list)
    traffic_file = "output_data/traffic_logs.csv"
    
    # Quan trọng: Ghi format chuẩn ISO để pandas đọc nhanh, float 3 số lẻ cho nhẹ
    traffic_df.to_csv(traffic_file, index=False, encoding='utf-8', float_format='%.3f', date_format='%Y-%m-%d %H:%M:%S')
    
    end_time = time.time()
    print(f"\n================ HOÀN TẤT ===================")
    print(f"✅ File Traffic: {traffic_file}")
    print(f"📊 Kích thước: {len(traffic_df):,} dòng")
    print(f"🕒 Thời gian chạy: {end_time - start_time:.2f}s")
    print(f"=============================================")

if __name__ == "__main__":
    import numpy as np
    import random
    np.random.seed(config.SEED)
    random.seed(config.SEED)
    main()