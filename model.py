import torch
import torch.nn as nn
import torch.nn.functional as F

class GraphConvLayer(nn.Module):
    def __init__(self, in_features, out_features):
        super(GraphConvLayer, self).__init__()
        self.linear = nn.Linear(in_features, out_features)

    def forward(self, x, adj):
        # x: (Batch, Nodes, Features)
        # adj: (Nodes, Nodes)
        
        # 1. Spatial Aggregation: AX (Matrix multiplication)
        # Batch matric mul: (Batch, Nodes, Feat) -> Transpose to handle correctly if needed
        # Nhưng đơn giản nhất: Support = AX
        support = torch.matmul(adj, x) # (Batch, Nodes, Features)
        
        # 2. Linear Transform
        output = self.linear(support)
        return output

class STGNN(nn.Module):
    def __init__(self, num_nodes, input_dim, hidden_dim, output_len, dropout=0.2):
        super(STGNN, self).__init__()
        self.num_nodes = num_nodes
        self.output_len = output_len
        
        # 1. Spatial Block (Graph Convolution)
        self.gcn = GraphConvLayer(input_dim, hidden_dim)
        
        # 2. Temporal Block (LSTM)
        # Input cho LSTM sẽ là output của GCN
        self.lstm = nn.LSTM(input_size=hidden_dim, 
                            hidden_size=hidden_dim, 
                            num_layers=2, 
                            batch_first=True, 
                            dropout=dropout)
        
        # 3. Output Layer
        # Predict output_len steps for each node
        self.fc = nn.Linear(hidden_dim, output_len)
        
    def forward(self, x, adj):
        # x shape: (Batch, Seq_Len, Nodes, Features)
        b, s, n, f = x.shape
        
        # Flatten batch và seq để qua GCN: (Batch*Seq, Nodes, Feats)
        x_reshaped = x.view(b*s, n, f)
        
        # Pass through GCN
        spatial_out = F.relu(self.gcn(x_reshaped, adj)) # (Batch*Seq, Nodes, Hidden)
        
        # Reshape lại để vào LSTM: (Batch, Seq, Nodes*Hidden) -> Không, LSTM cần (Batch, Seq, Feature)
        # Chúng ta muốn dự đoán cho từng Node, nên coi mỗi Node là một sample trong batch hoặc dùng shared weights.
        # Cách tốt nhất cho bài toán này: Permute để (Batch * Nodes, Seq, Hidden)
        spatial_out = spatial_out.view(b, s, n, -1)
        spatial_out = spatial_out.permute(0, 2, 1, 3).contiguous().view(b*n, s, -1)
        
        # Pass through LSTM
        lstm_out, _ = self.lstm(spatial_out) # (Batch*Nodes, Seq, Hidden)
        
        # Lấy hidden state cuối cùng
        last_hidden = lstm_out[:, -1, :] # (Batch*Nodes, Hidden)
        
        # Prediction
        out = self.fc(last_hidden) # (Batch*Nodes, Output_Len)
        
        # Reshape lại về (Batch, Output_Len, Nodes)
        out = out.view(b, n, self.output_len).permute(0, 2, 1) # (Batch, P_Len, Nodes)
        
        return out