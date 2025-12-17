import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import os

import train_config as cfg
from dataset import load_data, TrafficDataset
from model import STGNN

def evaluate(model, loader, adj, criterion):
    model.eval()
    total_loss = 0
    with torch.no_grad():
        for x, y in loader:
            x = x.to(cfg.DEVICE)
            y = y.to(cfg.DEVICE) # (Batch, Pred_Len, Nodes)
            
            preds = model(x, adj)
            loss = criterion(preds, y)
            total_loss += loss.item()
    return total_loss / len(loader)

def main():
    # 1. Prepare Data
    (X_train, Y_train), (X_val, Y_val), _, adj_matrix, scaler, _ = load_data()
    
    train_loader = DataLoader(TrafficDataset(X_train, Y_train), batch_size=cfg.BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(TrafficDataset(X_val, Y_val), batch_size=cfg.BATCH_SIZE, shuffle=False)
    
    # 2. Init Model
    model = STGNN(num_nodes=cfg.NUM_NODES, 
                  input_dim=cfg.INPUT_DIM, 
                  hidden_dim=cfg.HIDDEN_DIM, 
                  output_len=cfg.PRED_LEN,
                  dropout=cfg.DROPOUT).to(cfg.DEVICE)
    
    optimizer = optim.Adam(model.parameters(), lr=cfg.LEARNING_RATE)
    criterion = nn.MSELoss()
    
    print(f"Dataset Size: {len(X_train)} samples")
    print(">>> Start Training...")
    
    best_val_loss = float('inf')
    
    for epoch in range(cfg.EPOCHS):
        model.train()
        train_loss = 0
        
        for x, y in train_loader:
            x = x.to(cfg.DEVICE)
            y = y.to(cfg.DEVICE)
            
            optimizer.zero_grad()
            preds = model(x, adj_matrix) # Forward pass
            
            loss = criterion(preds, y)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            
        avg_train_loss = train_loss / len(train_loader)
        avg_val_loss = evaluate(model, val_loader, adj_matrix, criterion)
        
        print(f"Epoch {epoch+1}/{cfg.EPOCHS} | Train Loss: {avg_train_loss:.6f} | Val Loss: {avg_val_loss:.6f}")
        
        # Save Best Model
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            if not os.path.exists("output_model"):
                os.makedirs("output_model")
            torch.save(model.state_dict(), cfg.MODEL_SAVE_PATH)
            print("  --> Saved Best Model")

if __name__ == "__main__":
    main()