import torch
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pandas as pd

import train_config as cfg
from dataset import load_data, TrafficDataset
from model import STGNN

def compute_metrics(y_true, y_pred):
    # Masking: Chỉ tính lỗi ở những điểm có traffic > 0.1 để tránh chia cho 0
    mask = y_true > 0.1
    if np.sum(mask) == 0:
        return 0, 0, 0
        
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    mae = mean_absolute_error(y_true.flatten(), y_pred.flatten())
    rmse = np.sqrt(mean_squared_error(y_true.flatten(), y_pred.flatten()))
    return mae, rmse, mape

def run_inference():
    # 1. Load Data
    # Lưu ý: Hàm load_data trả về full data, ta chỉ cần test set
    _, _, (X_test, Y_test), adj_matrix, scaler, node_names = load_data()
    
    # 2. Load Model
    print(">>> Loading Model...")
    model = STGNN(num_nodes=cfg.NUM_NODES, 
                  input_dim=cfg.INPUT_DIM, 
                  hidden_dim=cfg.HIDDEN_DIM, 
                  output_len=cfg.PRED_LEN).to(cfg.DEVICE)
    
    try:
        model.load_state_dict(torch.load(cfg.MODEL_SAVE_PATH, map_location=cfg.DEVICE))
    except FileNotFoundError:
        print(f"❌ Error: Không tìm thấy file model tại {cfg.MODEL_SAVE_PATH}")
        print("   Vui lòng chạy 'train.py' trước!")
        return

    model.eval()
    
    # 3. Batch Inference (FIX OOM ERROR)
    # Thay vì đưa cả cục X_test vào, ta dùng DataLoader để chạy từng batch
    print(">>> Running Inference (Batch processing)...")
    
    test_dataset = TrafficDataset(X_test, Y_test)
    test_loader = DataLoader(test_dataset, batch_size=cfg.BATCH_SIZE, shuffle=False)
    
    all_preds = []
    all_targets = []
    
    with torch.no_grad():
        for x, y in test_loader:
            x = x.to(cfg.DEVICE)
            # y không cần đưa lên GPU vì ta chỉ cần nó để so sánh kết quả cuối cùng
            
            # Dự đoán
            pred_batch = model(x, adj_matrix)
            
            # Quan trọng: Chuyển ngay về CPU để giải phóng VRAM GPU
            all_preds.append(pred_batch.cpu())
            all_targets.append(y)

    # Nối các batch lại thành 1 cục lớn
    preds = torch.cat(all_preds, dim=0).numpy() # (Total_Samples, Pred_Len, Nodes)
    Y_true = torch.cat(all_targets, dim=0).numpy()
    
    print(f"✅ Inference Done. Shape: {preds.shape}")

    # 4. Inverse Scaling (Đưa về đơn vị Mbps thực tế)
    print(">>> Calculating Metrics...")
    
    # Logic Inverse Scale:
    # Scaler được fit với shape (Samples, Nodes).
    # Preds đang là (Samples, Pred_Len, Nodes).
    # Ta phải loop qua từng time-step dự báo để inverse.
    
    preds_inv = np.zeros_like(preds)
    Y_true_inv = np.zeros_like(Y_true)
    
    for i in range(cfg.PRED_LEN):
        # Lấy slice tại bước dự báo thứ i: (Samples, Nodes)
        p_slice = preds[:, i, :]
        y_slice = Y_true[:, i, :]
        
        # Inverse transform
        preds_inv[:, i, :] = scaler.inverse_transform(p_slice)
        Y_true_inv[:, i, :] = scaler.inverse_transform(y_slice)
    
    # 5. Evaluate
    mae, rmse, mape = compute_metrics(Y_true_inv, preds_inv)
    print(f"\n================ EVALUATION METRICS ================")
    print(f"MAE  : {mae:.2f} Mbps")
    print(f"RMSE : {rmse:.2f} Mbps")
    print(f"MAPE : {mape:.2f} %")
    print(f"====================================================")
    
    # 6. Visualization
    # Chọn ngẫu nhiên 1 mẫu để vẽ
    import random
    sample_idx = random.randint(0, len(X_test) - 1)
    node_idx = 0 # Vẽ node đầu tiên
    node_name = node_names[node_idx]
    
    # Lấy lịch sử (Input) - Cần inverse scale
    history_norm = X_test[sample_idx, :, node_idx, 0] # Feature 0 is traffic
    # Trick để inverse 1 chiều: tạo dummy array
    dummy = np.zeros((len(history_norm), cfg.NUM_NODES)) # type: ignore
    dummy[:, node_idx] = history_norm
    history_real = scaler.inverse_transform(dummy)[:, node_idx]
    
    # Lấy Ground Truth & Pred (đã inverse ở trên)
    future_real = Y_true_inv[sample_idx, :, node_idx]
    future_pred = preds_inv[sample_idx, :, node_idx]
    
    plt.figure(figsize=(10, 6))
    
    t_hist = range(0, cfg.SEQ_LEN)
    t_fut = range(cfg.SEQ_LEN, cfg.SEQ_LEN + cfg.PRED_LEN)
    
    plt.plot(t_hist, history_real, 'b-o', label='History (Past 3h)')
    plt.plot(t_fut, future_real, 'g-o', label='Actual (Next 1h)')
    plt.plot(t_fut, future_pred, 'r--x', label='Forecast (ST-GNN)')
    
    plt.axvline(x=cfg.SEQ_LEN - 0.5, color='gray', linestyle='--', alpha=0.5)
    plt.title(f"Forecast for Node: {node_name}\nSample ID: {sample_idx}")
    plt.xlabel("Time Steps (15 mins)")
    plt.ylabel("Bandwidth (Mbps)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_inference()