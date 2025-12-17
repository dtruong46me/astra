import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
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
    """
    Tạo ma trận kề (A) chuẩn hóa từ danh sách cạnh.
    A_wave = D^-1/2 * (A + I) * D^-1/2
    """
    num_nodes = len(nodes)
    node_map = {node: i for i, node in enumerate(nodes)}
    
    # Khởi tạo ma trận toàn số 0
    adj = np.zeros((num_nodes, num_nodes))
    
    # Fill ma trận dựa trên topology file
    for _, row in topo_df.iterrows():
        if row['source_device'] in node_map and row['target_device'] in node_map:
            u = node_map[row['source_device']]
            v = node_map[row['target_device']]
            adj[u, v] = 1
            adj[v, u] = 1 # Vô hướng
            
    # Self-loop (Thêm ma trận đơn vị I)
    adj = adj + np.eye(num_nodes)
    
    # Normalize (Laplacian normalization)
    row_sum = adj.sum(1)
    d_inv_sqrt = np.power(row_sum, -0.5)
    d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.
    d_mat_inv_sqrt = np.diag(d_inv_sqrt)
    
    norm_adj = d_mat_inv_sqrt.dot(adj).dot(d_mat_inv_sqrt)
    return torch.FloatTensor(norm_adj).to(cfg.DEVICE)

def feature_engineering(df_pivot):
    """
    Tạo thêm các feature: Time of Day, Day of Week, Holiday
    """
    timestamps = df_pivot.index
    
    # 1. Time Features (Cyclical encoding)
    hour = timestamps.hour.values
    day_of_week = timestamps.dayofweek.values
    
    hour_sin = np.sin(2 * np.pi * hour / 24)
    hour_cos = np.cos(2 * np.pi * hour / 24)
    day_sin = np.sin(2 * np.pi * day_of_week / 7)
    day_cos = np.cos(2 * np.pi * day_of_week / 7)
    
    # 2. Event Feature
    is_holiday = np.zeros(len(timestamps))
    date_strs = timestamps.strftime('%Y-%m-%d')
    
    for i, d in enumerate(date_strs):
        if d in cfg.HOLIDAYS_ISO or d in cfg.SPECIAL_EVENTS_ISO:
            is_holiday[i] = 1.0
            
    # Mở rộng kích thước để khớp với (Time, Nodes, Features)
    # Traffic shape: (Time, Nodes) -> Chúng ta cần ghép feature vào từng node
    num_nodes = df_pivot.shape[1]
    
    # Feature array: (Time, Num_Features)
    feature_array = np.stack([hour_sin, hour_cos, day_sin, day_cos, is_holiday], axis=1)
    
    # Repeat feature cho tất cả các node: (Time, Nodes, Features)
    # Traffic là feature đầu tiên
    traffic_values = df_pivot.values # (Time, Nodes)
    
    # Reshape features to (Time, 1, Feats) then broadcast
    feature_expanded = np.tile(feature_array[:, np.newaxis, :], (1, num_nodes, 1))
    
    # Combine: Traffic (Time, Nodes, 1) + Features (Time, Nodes, 5)
    full_data = np.concatenate([traffic_values[:, :, np.newaxis], feature_expanded], axis=2)
    
    return full_data, traffic_values # Trả về full features và raw traffic (để làm label)

def load_data():
    print(">>> Loading Data...")
    df_traffic = pd.read_csv(cfg.TRAFFIC_PATH)
    df_topo = pd.read_csv(cfg.TOPO_PATH)
    
    df_traffic['timestamp'] = pd.to_datetime(df_traffic['timestamp'])
    
    # Pivot: Index=Time, Col=NodeID, Val=Bandwidth
    df_pivot = df_traffic.pivot(index='timestamp', columns='device_id', values='bandwidth_usage_mbps')
    df_pivot = df_pivot.fillna(method='ffill').fillna(0) # Handle missing # type: ignore
    
    nodes = df_pivot.columns.tolist()
    cfg.NUM_NODES = len(nodes)
    
    # Lấy Ma trận kề
    adj_matrix = get_adjacency_matrix(nodes, df_topo)
    
    # Scale dữ liệu Traffic (Chỉ scale feature traffic, các feature khác đã ở range tốt)
    scaler = StandardScaler()
    # Fit scaler trên toàn bộ traffic data (trong thực tế chỉ nên fit trên train)
    scaled_traffic = scaler.fit_transform(df_pivot.values)
    
    # Thay thế cột traffic cũ bằng cột đã scale
    full_data, _ = feature_engineering(df_pivot)
    full_data[:, :, 0] = scaled_traffic 
    
    # Tạo Sliding Window
    X, Y = [], []
    # Y chỉ cần predict Traffic (feature 0)
    
    L = len(df_pivot)
    for i in range(L - cfg.SEQ_LEN - cfg.PRED_LEN):
        X.append(full_data[i : i + cfg.SEQ_LEN]) # (Seq_Len, Nodes, Feats)
        Y.append(full_data[i + cfg.SEQ_LEN : i + cfg.SEQ_LEN + cfg.PRED_LEN, :, 0]) # (Pred_Len, Nodes)
        
    X = np.array(X)
    Y = np.array(Y)
    
    # Split Train/Test
    train_size = int(len(X) * cfg.TRAIN_RATIO)
    val_size = int(len(X) * cfg.VAL_RATIO)
    
    X_train, Y_train = X[:train_size], Y[:train_size]
    X_val, Y_val = X[train_size : train_size+val_size], Y[train_size : train_size+val_size]
    X_test, Y_test = X[train_size+val_size:], Y[train_size+val_size:]
    
    print(f"Data Shapes: Train {X_train.shape}, Val {X_val.shape}, Test {X_test.shape}")
    
    return (X_train, Y_train), (X_val, Y_val), (X_test, Y_test), adj_matrix, scaler, nodes