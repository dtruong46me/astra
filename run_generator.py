# main.py
import config
import generator
import os
import time

def main():
    start_time = time.time()
    
    # Tạo thư mục output nếu chưa có
    if not os.path.exists("output_data"):
        os.makedirs("output_data")

    # 1. Sinh Topology
    topo_df, node_list = generator.generate_topology()
    topo_file = "output_data/network_topology.csv"
    topo_df.to_csv(topo_file, index=False)
    print(f"✅ Đã tạo file Topology: {topo_file} ({len(topo_df)} links)")

    # 2. Sinh Traffic Logs
    traffic_df = generator.generate_traffic_data(node_list)
    traffic_file = "output_data/traffic_logs.csv"
    traffic_df.to_csv(traffic_file, index=False)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n================ KẾT QUẢ ===================")
    print(f"✅ Đã tạo file Traffic: {traffic_file}")
    print(f"📊 Tổng số dòng dữ liệu: {len(traffic_df):,}")
    print(f"🕒 Thời gian thực thi: {duration:.2f} giây")
    print(f"============================================")
    print(f"Gợi ý: Dùng file 'traffic_logs.csv' để train model Prophet/LSTM.")
    print(f"Gợi ý: Dùng file 'network_topology.csv' để xây dựng Adjacency Matrix cho GNN.")

if __name__ == "__main__":
    # Set seed
    import numpy as np
    import random
    np.random.seed(config.SEED)
    random.seed(config.SEED)
    
    main()