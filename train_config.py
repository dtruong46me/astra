import torch

# Paths
TRAFFIC_PATH = "output_data/traffic_logs.csv"
TOPO_PATH = "output_data/network_topology.csv"
MODEL_SAVE_PATH = "output_model/best_stgnn_model.pth"

# Data Parameters
SEQ_LEN = 12       # Input window: Dùng 12 điểm quá khứ (3 tiếng nếu freq=15p)
PRED_LEN = 4       # Output horizon: Dự báo 4 điểm tương lai (1 tiếng)
TRAIN_RATIO = 0.7  # 70% Train
VAL_RATIO = 0.15   # 15% Validation, 15% Test

# Model Hyperparameters
INPUT_DIM = 6      # Số lượng feature đầu vào (Traffic + Time features + Holiday flag)
HIDDEN_DIM = 64    # Số nơ-ron lớp ẩn
NUM_NODES = None   # Sẽ tự động cập nhật khi load data
DROPOUT = 0.2
LEARNING_RATE = 0.001
BATCH_SIZE = 32
EPOCHS = 50

# Device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Events Config (Copy lại logic ngày lễ để đánh nhãn feature)
HOLIDAYS_ISO = [
    "2023-01-20", "2023-01-21", "2023-01-22", "2023-01-23", # Tết 2023
    "2024-02-08", "2024-02-09", "2024-02-10"  # Tết 2024
]
SPECIAL_EVENTS_ISO = ["2023-11-24", "2023-05-15"] # Black Friday, Football