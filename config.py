# config.py
import pandas as pd

# ==========================================
# 1. CẤU HÌNH THỜI GIAN (TIME CONFIG)
# ==========================================
# Ngày bắt đầu và kết thúc (Nên để dài khoảng 1-2 năm để model học được mùa vụ)
START_DATE = "2023-01-01"
END_DATE = "2024-12-31"
# Tần suất lấy mẫu (15 phút/mẫu là chuẩn cho bài toán quy hoạch)
FREQUENCY = "15min" 

# ==========================================
# 2. CẤU HÌNH HẠ TẦNG (TOPOLOGY CONFIG)
# ==========================================
# Số lượng vòng Ring (Mỗi Ring đại diện cho một khu vực)
NUM_RINGS = 5 
# Số lượng Node trung bình trên mỗi Ring
NODES_PER_RING = 10
# Dung lượng vật lý của đường truyền (Mbps) - Ví dụ 10Gbps
LINK_CAPACITY_MBPS = 10000 
# Tỉ lệ kết nối chéo giữa các Ring (để tạo cấu trúc đồ thị phức tạp hơn)
INTER_RING_CONNECTIVITY = 0.2 

# ==========================================
# 3. CẤU HÌNH LƯU LƯỢNG (TRAFFIC PATTERN)
# ==========================================
# Lưu lượng nền trung bình (Mbps)
BASE_TRAFFIC_MEAN = 4000 
# Độ lệch chuẩn (để tạo dao động ngẫu nhiên)
BASE_TRAFFIC_STD = 500
# Xu hướng tăng trưởng mạng lưới theo năm (Linear Trend) - Ví dụ tăng 10% mỗi năm
YEARLY_GROWTH_RATE = 0.10 
# Random Seed để tái lập kết quả
SEED = 42

# ==========================================
# 4. SỰ KIỆN & NGÀY LỄ (EVENTS & HOLIDAYS)
# ==========================================
# Định nghĩa các khoảng thời gian đặc biệt ảnh hưởng đến traffic
# impact_factor: Hệ số nhân (1.5 nghĩa là tăng 50%, 0.6 là giảm 40%)
SPECIAL_EVENTS = [
    # Tết Nguyên Đán 2023 (Giả lập giảm tải ở TP lớn do về quê)
    {
        "name": "Tet_Holiday_2023",
        "start": "2023-01-20", 
        "end": "2023-01-26", 
        "impact_factor": 0.6, 
        "type": "holiday"
    },
    # Tết Nguyên Đán 2024
    {
        "name": "Tet_Holiday_2024",
        "start": "2024-02-08", 
        "end": "2024-02-14", 
        "impact_factor": 0.6,
        "type": "holiday"
    },
    # Sự kiện Black Friday (Tăng mua sắm online -> Tăng traffic)
    {
        "name": "Black_Friday_2023",
        "start": "2023-11-24 00:00",
        "end": "2023-11-24 23:59",
        "impact_factor": 1.4,
        "type": "event"
    },
    # Trận chung kết bóng đá (Spike cực mạnh trong vài giờ)
    {
        "name": "Football_Final_Match",
        "start": "2023-05-15 19:00",
        "end": "2023-05-15 22:00",
        "impact_factor": 1.8, # Tăng 80%
        "type": "spike"
    }
]