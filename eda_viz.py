import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import train_config as cfg

def run_eda():
    print(">>> Đang đọc dữ liệu để Visualize...")
    df_traffic = pd.read_csv(cfg.TRAFFIC_PATH)
    df_topo = pd.read_csv(cfg.TOPO_PATH)
    
    df_traffic['timestamp'] = pd.to_datetime(df_traffic['timestamp'])
    
    # 1. Vẽ Topology
    plt.figure(figsize=(10, 8))
    G = nx.from_pandas_edgelist(df_topo, 'source_device', 'target_device', ['distance_km'])
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_size=300, node_color='skyblue', font_size=8)
    plt.title("Network Topology Structure")
    plt.show()

    # Save topology figure
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=300, node_color='skyblue', font_size=8)
    plt.title("Network Topology Structure")
    plt.savefig("output_data/network_topology_visualization.png")
    plt.close()

    # 2. Vẽ Traffic của 1 Node tiêu biểu
    sample_node = df_traffic['device_id'].unique()[0]
    df_node = df_traffic[df_traffic['device_id'] == sample_node].set_index('timestamp')
    
    plt.figure(figsize=(15, 5))
    plt.plot(df_node['bandwidth_usage_mbps'][:500], label='Traffic (Mbps)')
    plt.title(f"Traffic Pattern of Node: {sample_node} (First 500 points)")
    plt.legend()
    plt.grid(True)
    plt.show()

    # Save traffic figure
    plt.figure(figsize=(15, 5))
    plt.plot(df_node['bandwidth_usage_mbps'][:500], label='Traffic (Mbps)')
    plt.title(f"Traffic Pattern of Node: {sample_node} (First 500 points)")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"output_data/traffic_pattern_{sample_node}.png")
    plt.close()

    # 3. Heatmap tương quan giữa các Node (Spatial Correlation)
    # Pivot table: Index=Time, Columns=Nodes
    df_pivot = df_traffic.pivot(index='timestamp', columns='device_id', values='bandwidth_usage_mbps')
    
    plt.figure(figsize=(12, 10))
    # Lấy mẫu 20 node đầu tiên để vẽ cho đỡ rối
    sns.heatmap(df_pivot.iloc[:, :20].corr(), cmap='coolwarm', annot=False)
    plt.title("Spatial Correlation Matrix (First 20 Nodes)")
    plt.show()

    # Save heatmap figure
    plt.figure(figsize=(12, 10))
    sns.heatmap(df_pivot.iloc[:, :20].corr(), cmap='coolwarm', annot=False)
    plt.title("Spatial Correlation Matrix (First 20 Nodes)")
    plt.savefig("output_data/spatial_correlation_heatmap.png")
    plt.close()
    
    print("EDA Complete.")

if __name__ == "__main__":
    run_eda()