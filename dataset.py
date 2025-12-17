# dataset.py
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
from sklearn.preprocessing import StandardScaler
import train_config as cfg

class TrafficDataset(Dataset):
    def __init__(self, X, Y):
        self.X = torch.FloatTensor(X)
        self.Y = torch.FloatTensor(Y)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.Y[idx]

def get_adjacency_matrix(nodes, topo_df):
    num_nodes = len(nodes)
    node_map = {node: i for i, node in enumerate(nodes)}
    adj = np.zeros((num_nodes, num_nodes))
    
    for _, row in topo_df.iterrows():
        if row['source_device'] in node_map and row['target_device'] in node_map:
            u = node_map[row['source_device']]
            v = node_map[row['target_device']]
            adj[u, v] = 1
            adj[v, u] = 1 
            
    adj = adj + np.eye(num_nodes)
    row_sum = adj.sum(1)
    with np.errstate(divide='ignore'):
        d_inv_sqrt = np.power(row_sum, -0.5)
    d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.
    d_mat_inv_sqrt = np.diag(d_inv_sqrt)
    norm_adj = d_mat_inv_sqrt.dot(adj).dot(d_mat_inv_sqrt)
    return torch.FloatTensor(norm_adj).to(cfg.DEVICE)

def feature_engineering(df_pivot):
    timestamps = df_pivot.index
    # Time Features
    hour = timestamps.hour.values
    day_of_week = timestamps.dayofweek.values
    
    hour_sin = np.sin(2 * np.pi * hour / 24)
    hour_cos = np.cos(2 * np.pi * hour / 24)
    day_sin = np.sin(2 * np.pi * day_of_week / 7)
    day_cos = np.cos(2 * np.pi * day_of_week / 7)
    
    # Event Feature
    is_holiday = np.zeros(len(timestamps))
    date_strs = timestamps.strftime('%Y-%m-%d')
    holidays_set = set(cfg.HOLIDAYS_ISO)
    events_set = set(cfg.SPECIAL_EVENTS_ISO)
    
    for i, d in enumerate(date_strs):
        if d in holidays_set or d in events_set:
            is_holiday[i] = 1.0
            
    num_nodes = df_pivot.shape[1]
    feature_array = np.stack([hour_sin, hour_cos, day_sin, day_cos, is_holiday], axis=1)
    feature_expanded = np.tile(feature_array[:, np.newaxis, :], (1, num_nodes, 1))
    traffic_values = df_pivot.values 
    full_data = np.concatenate([traffic_values[:, :, np.newaxis], feature_expanded], axis=2)
    return full_data

def load_data():
    print(">>> Loading Data...")
    
    # 1. Đọc dữ liệu an toàn
    # on_bad_lines='skip': Bỏ qua dòng bị lỗi format trong CSV
    try:
        df_traffic = pd.read_csv(cfg.TRAFFIC_PATH, on_bad_lines='skip')
    except:
        df_traffic = pd.read_csv(cfg.TRAFFIC_PATH, error_bad_lines=False) # type: ignore

    df_topo = pd.read_csv(cfg.TOPO_PATH)
    
    # 2. Xử lý Date Time cực kỳ cẩn thận
    # errors='coerce': Nếu format sai, biến thành NaT chứ không báo lỗi
    df_traffic['timestamp'] = pd.to_datetime(df_traffic['timestamp'], errors='coerce')
    
    # Bỏ các dòng bị NaT (do lỗi parse)
    original_len = len(df_traffic)
    df_traffic = df_traffic.dropna(subset=['timestamp'])
    if len(df_traffic) < original_len:
        print(f"⚠️ Warning: Đã loại bỏ {original_len - len(df_traffic)} dòng lỗi thời gian.")

    # 3. Xử lý trùng lặp (Đây là thuốc chữa bệnh treo máy lúc pivot)
    # Nếu có 2 dòng cùng timestamp và device_id, giữ dòng cuối cùng
    df_traffic = df_traffic.drop_duplicates(subset=['timestamp', 'device_id'], keep='last')

    # 4. Pivot
    print(">>> Pivoting data (Might take a moment)...")
    df_pivot = df_traffic.pivot(index='timestamp', columns='device_id', values='bandwidth_usage_mbps')
    
    # 5. Fill missing data
    df_pivot = df_pivot.ffill().fillna(0)
    df_pivot = df_pivot.sort_index()

    nodes = df_pivot.columns.tolist()
    cfg.NUM_NODES = len(nodes)
    
    adj_matrix = get_adjacency_matrix(nodes, df_topo)
    
    scaler = StandardScaler()
    scaled_traffic = scaler.fit_transform(df_pivot.values)
    
    full_data = feature_engineering(df_pivot)
    full_data[:, :, 0] = scaled_traffic 
    full_data = np.array(full_data, dtype=np.float32)
    
    # Sliding Window
    X, Y = [], []
    L = len(df_pivot)
    for i in range(L - cfg.SEQ_LEN - cfg.PRED_LEN):
        X.append(full_data[i : i + cfg.SEQ_LEN]) 
        Y.append(full_data[i + cfg.SEQ_LEN : i + cfg.SEQ_LEN + cfg.PRED_LEN, :, 0]) 
        
    X = np.array(X)
    Y = np.array(Y)
    
    train_size = int(len(X) * cfg.TRAIN_RATIO)
    val_size = int(len(X) * cfg.VAL_RATIO)
    
    X_train, Y_train = X[:train_size], Y[:train_size]
    X_val, Y_val = X[train_size : train_size+val_size], Y[train_size : train_size+val_size]
    X_test, Y_test = X[train_size+val_size:], Y[train_size+val_size:]
    
    print(f"Data Shapes: Train {X_train.shape}, Val {X_val.shape}, Test {X_test.shape}")
    
    return (X_train, Y_train), (X_val, Y_val), (X_test, Y_test), adj_matrix, scaler, nodes