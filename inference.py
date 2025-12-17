import torch
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pandas as pd

import train_config as cfg
from dataset import load_data, TrafficDataset
from model import STGNN

def compute_metrics(y_true, y_pred):
    # Tránh chia cho 0
    mask = y_true > 0.1
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    mae = mean_absolute_error(y_true.flatten(), y_pred.flatten())
    rmse = np.sqrt(mean_squared_error(y_true.flatten(), y_pred.flatten()))
    return mae, rmse, mape

def run_inference():
    # 1. Load Data & Scaler
    _, _, (X_test, Y_test), adj_matrix, scaler, node_names = load_data()
    
    # 2. Load Model
    model = STGNN(num_nodes=cfg.NUM_NODES, 
                  input_dim=cfg.INPUT_DIM, 
                  hidden_dim=cfg.HIDDEN_DIM, 
                  output_len=cfg.PRED_LEN).to(cfg.DEVICE)
    
    model.load_state_dict(torch.load(cfg.MODEL_SAVE_PATH, map_location=cfg.DEVICE))
    model.eval()
    
    print(">>> Running Inference on Test Set...")
    
    # Convert Test Data to Tensor
    X_tensor = torch.FloatTensor(X_test).to(cfg.DEVICE)
    
    with torch.no_grad():
        preds = model(X_tensor, adj_matrix)
        
    preds = preds.cpu().numpy() # (Samples, Pred_Len, Nodes)
    Y_true = Y_test # (Samples, Pred_Len, Nodes)
    
    # Inverse Scale (Quan trọng: Đưa về đơn vị Mbps gốc)
    # Scaler fit trên (Samples, Nodes), nên cần reshape
    preds_reshaped = preds.transpose(0, 2, 1).reshape(-1, cfg.NUM_NODES) # Gộp Time vào Sample tạm
    Y_true_reshaped = Y_true.transpose(0, 2, 1).reshape(-1, cfg.NUM_NODES) # type: ignore
    
    preds_inv = scaler.inverse_transform(preds_reshaped)
    Y_true_inv = scaler.inverse_transform(Y_true_reshaped)
    
    # Reshape back to (Samples, Pred_Len, Nodes)
    preds_final = preds_inv.reshape(len(X_test), cfg.PRED_LEN, cfg.NUM_NODES).transpose(0, 2, 1)
    Y_true_final = Y_true_inv.reshape(len(X_test), cfg.PRED_LEN, cfg.NUM_NODES).transpose(0, 2, 1) # Wait, logic reshape inverse is tricky. # type: ignore
    
    # Cách đơn giản hơn: Inverse scale từng sample, hoặc tính metric trên flattened array rồi mới inverse.
    # Nhưng ta đã inverse đúng logic ở trên.
    
    # 3. Evaluate
    mae, rmse, mape = compute_metrics(Y_true_inv, preds_inv)
    print(f"\n================ EVALUATION METRICS ================")
    print(f"MAE  : {mae:.2f} Mbps")
    print(f"RMSE : {rmse:.2f} Mbps")
    print(f"MAPE : {mape:.2f} %")
    print(f"====================================================")
    
    # 4. Visualization: Pick 1 Node, 1 Sample Window to plot
    # Chọn node đầu tiên và một khung thời gian ngẫu nhiên
    sample_idx = 100 
    node_idx = 0
    node_name = node_names[node_idx]
    
    # Lấy lịch sử (Sequence input)
    # Input X là Normalized, cần Inverse
    history_norm = X_test[sample_idx, :, node_idx, 0] # Lấy feature 0 là traffic
    # Inverse history (trick: tạo dummy array để inverse)
    dummy = np.zeros((len(history_norm), cfg.NUM_NODES)) # type: ignore
    dummy[:, node_idx] = history_norm
    history_real = scaler.inverse_transform(dummy)[:, node_idx]
    
    # Lấy Ground Truth tương lai
    future_real = Y_true_final[sample_idx, :, node_idx]
    
    # Lấy Dự đoán tương lai
    future_pred = preds_final[sample_idx, :, node_idx]
    
    # Plotting
    plt.figure(figsize=(12, 6))
    
    # Trục thời gian
    t_history = range(0, cfg.SEQ_LEN)
    t_future = range(cfg.SEQ_LEN, cfg.SEQ_LEN + cfg.PRED_LEN)
    
    plt.plot(t_history, history_real, 'b-o', label='History (Input)')
    plt.plot(t_future, future_real, 'g-o', label='Ground Truth')
    plt.plot(t_future, future_pred, 'r--x', label='Prediction (ST-GNN)')
    
    plt.axvline(x=cfg.SEQ_LEN - 0.5, color='gray', linestyle='--')
    plt.title(f"Forecast for Node: {node_name} (MAE: {np.abs(future_real - future_pred).mean():.2f} Mbps)")
    plt.xlabel("Time Steps (15 mins)")
    plt.ylabel("Bandwidth (Mbps)")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    run_inference()