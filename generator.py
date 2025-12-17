# generator.py
import pandas as pd
import numpy as np
import networkx as nx
import random
from datetime import timedelta
import config

def generate_topology():
    """
    Sinh ra cấu trúc mạng lưới (Graph Topology) dạng Ring + Cross-connect.
    Output: DataFrame chứa danh sách liên kết (Edges).
    """
    print(">>> Đang khởi tạo Topology hạ tầng...")
    G = nx.Graph()
    all_nodes = []

    # 1. Tạo các Ring riêng biệt
    for r in range(config.NUM_RINGS):
        ring_nodes = [f"PTN_RING{r+1:02d}_{n+1:02d}" for n in range(config.NODES_PER_RING)]
        all_nodes.extend(ring_nodes)
        
        # Tạo kết nối vòng tròn (Ring)
        for i in range(len(ring_nodes)):
            u = ring_nodes[i]
            v = ring_nodes[(i + 1) % len(ring_nodes)] # Nối node cuối về node đầu
            dist = round(random.uniform(2.0, 15.0), 1) # Khoảng cách ngẫu nhiên 2-15km
            G.add_edge(u, v, weight=dist, type="Fiber_Ring")

    # 2. Tạo kết nối chéo giữa các Ring (Inter-ring links)
    num_cross_links = int(len(all_nodes) * config.INTER_RING_CONNECTIVITY)
    for _ in range(num_cross_links):
        u = random.choice(all_nodes)
        v = random.choice(all_nodes)
        if u != v and not G.has_edge(u, v):
            dist = round(random.uniform(10.0, 50.0), 1)
            G.add_edge(u, v, weight=dist, type="Fiber_Cross")

    # Xuất ra DataFrame
    edges = []
    for u, v, data in G.edges(data=True):
        edges.append({
            "source_device": u,
            "target_device": v,
            "connection_type": data["type"],
            "distance_km": data["weight"],
            "link_capacity_mbps": config.LINK_CAPACITY_MBPS
        })
    
    return pd.DataFrame(edges), all_nodes

def generate_traffic_data(node_list):
    """
    Sinh dữ liệu Time-series lưu lượng cho từng Node.
    Sử dụng vectorization để xử lý nhanh lượng dữ liệu lớn.
    """
    print(f">>> Đang sinh dữ liệu Traffic từ {config.START_DATE} đến {config.END_DATE}...")
    
    # 1. Tạo trục thời gian
    time_index = pd.date_range(start=config.START_DATE, end=config.END_DATE, freq=config.FREQUENCY)
    n_steps = len(time_index)
    n_nodes = len(node_list)
    
    print(f"    - Tổng số Time-steps: {n_steps}")
    print(f"    - Tổng số Nodes: {n_nodes}")
    print(f"    - Ước tính tổng record: {n_steps * n_nodes}")

    # 2. Tạo Pattern cơ sở (Daily + Weekly Seasonality)
    # t tính bằng giờ
    t = np.arange(n_steps) * (15 / 60) 
    
    # Chu kỳ ngày (24h) + Chu kỳ tuần (168h)
    daily_pattern = np.sin(2 * np.pi * t / 24) 
    weekly_pattern = 0.5 * np.sin(2 * np.pi * t / 168)
    
    # Xu hướng tăng trưởng (Trend)
    trend = np.linspace(0, config.YEARLY_GROWTH_RATE, n_steps)

    # 3. Áp dụng sự kiện (Events Injection)
    event_multiplier = np.ones(n_steps) # Mặc định là 1.0 (không đổi)
    
    # Map time_index sang array index để fill nhanh
    time_series_df = pd.DataFrame({'timestamp': time_index})
    
    for event in config.SPECIAL_EVENTS:
        start_ts = pd.to_datetime(event["start"])
        end_ts = pd.to_datetime(event["end"])
        
        # Tìm các index nằm trong khoảng sự kiện
        mask = (time_index >= start_ts) & (time_index <= end_ts)
        event_multiplier[mask] = event["impact_factor"]

    # 4. Sinh dữ liệu cho từng Node (có thêm random noise riêng cho mỗi node)
    traffic_logs = []
    
    # Base signal chung cho toàn mạng
    global_signal = config.BASE_TRAFFIC_MEAN * (1 + 0.3 * daily_pattern + 0.1 * weekly_pattern + trend) * event_multiplier

    # Để tối ưu, ta không loop qua từng dòng, mà loop qua từng node
    for node in node_list:
        # Mỗi node có một chút lệch pha (phase shift) và độ nhiễu riêng
        node_bias = np.random.normal(0, config.BASE_TRAFFIC_STD)
        node_noise = np.random.normal(0, config.BASE_TRAFFIC_STD * 0.5, n_steps)
        
        # Traffic của node = Global Signal + Node Bias + Node Noise
        node_traffic = global_signal + node_bias + node_noise
        
        # Xử lý biên (không âm và không vượt quá capacity)
        node_traffic = np.clip(node_traffic, 0, config.LINK_CAPACITY_MBPS)
        
        # Tạo DataFrame tạm cho node này
        df_node = pd.DataFrame({
            "timestamp": time_index,
            "device_id": node,
            "port_id": "GE_1/0/1", # Giả định 1 port chính
            "link_capacity_mbps": config.LINK_CAPACITY_MBPS,
            "bandwidth_usage_mbps": node_traffic.round(2)
        })
        
        # Giảm dung lượng RAM bằng cách chỉ lưu type cần thiết
        df_node["bandwidth_usage_mbps"] = df_node["bandwidth_usage_mbps"].astype(np.float32)
        
        traffic_logs.append(df_node)

    # Gộp tất cả lại (Concatenate)
    print(">>> Đang gộp dữ liệu...")
    final_df = pd.concat(traffic_logs, ignore_index=True)
    return final_df