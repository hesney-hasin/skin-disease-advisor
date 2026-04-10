import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import torch, torch.nn as nn
import numpy as np
from torch.utils.data import DataLoader, random_split, WeightedRandomSampler, Dataset
from torchvision import datasets
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
from app.model import build_model, NUM_CLASSES
from app.utils import get_transforms



class TransformSubset(Dataset):
    def __init__(self, subset, transform):
        self.subset = subset
        self.transform = transform

    def __getitem__(self, idx):
        img, label = self.subset[idx]
        return self.transform(img), label

    def __len__(self):
        return len(self.subset)



def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print(f"Epochs: {args.epochs} | ImgSize: {args.imgsz} | Batch: {args.batch} | Patience: {args.patience}")

    # Load WITHOUT any transform — transforms applied per-split below
    full_ds = datasets.ImageFolder(args.data_dir)
    n_val = int(len(full_ds) * 0.15)
    train_split, val_split = random_split(
        full_ds, [len(full_ds) - n_val, n_val],
        generator=torch.Generator().manual_seed(42)
    )

    # Each split gets its own transform — no shared-dataset bug
    train_ds = TransformSubset(train_split, get_transforms(True,  args.imgsz))
    val_ds   = TransformSubset(val_split,   get_transforms(False, args.imgsz))

    # WeightedRandomSampler — uses train_split.indices (still valid)
    targets = [full_ds.targets[i] for i in train_split.indices]
    class_counts = np.bincount(targets)
    weights = 1.0 / class_counts[targets]
    sampler = WeightedRandomSampler(weights, len(weights), replacement=True)

    train_loader = DataLoader(train_ds, batch_size=args.batch, sampler=sampler, num_workers=2)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch, shuffle=False,   num_workers=2)
    print(f"Train: {len(train_ds):,} Val: {len(val_ds):,}")

    cw = torch.FloatTensor(1.0 / class_counts).to(device)
    cw = cw / cw.sum() * NUM_CLASSES
    criterion = nn.CrossEntropyLoss(weight=cw, label_smoothing=0.1)

    model = build_model(NUM_CLASSES, freeze_backbone=True).to(device)
    optimizer = AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=args.lr, weight_decay=1e-4)
    scheduler = CosineAnnealingWarmRestarts(optimizer, T_0=10, T_mult=2)

    best_val_acc = 0.0
    epochs_no_improve = 0
    os.makedirs(args.output, exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        if epoch == 10:
            for p in model.features.parameters():
                p.requires_grad = True
            optimizer = AdamW(model.parameters(), lr=args.lr * 0.1, weight_decay=1e-4)
            scheduler = CosineAnnealingWarmRestarts(optimizer, T_0=10, T_mult=2)
            print("✓ Backbone unfrozen at epoch 10.")

        model.train()
        total_loss, correct, total = 0, 0, 0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            out = model(imgs)
            loss = criterion(out, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * imgs.size(0)
            correct += (out.argmax(1) == labels).sum().item()
            total += imgs.size(0)
        scheduler.step()

        model.eval()
        vc, vt = 0, 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(device), labels.to(device)
                vc += (model(imgs).argmax(1) == labels).sum().item()
                vt += imgs.size(0)
        val_acc = vc / vt
        print(f"Epoch {epoch:03d}/{args.epochs} loss={total_loss/total:.4f} "
              f"train_acc={correct/total:.4f} val_acc={val_acc:.4f}", flush=True)

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            epochs_no_improve = 0
            torch.save(model.state_dict(), os.path.join(args.output, "efficientnet_skin.pth"))
            print(f"  ✓ Best model saved! val_acc={val_acc:.4f}")
        else:
            epochs_no_improve += 1
            print(f"  No improvement. Patience: {epochs_no_improve}/{args.patience}")
            if epochs_no_improve >= args.patience:
                print(f"\n⏹ Early stopping at epoch {epoch}.")
                break

    print(f"\n🎉 Done! Best val accuracy: {best_val_acc:.4f} ({best_val_acc*100:.2f}%)")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", default="data")
    p.add_argument("--epochs",   type=int,   default=50)
    p.add_argument("--imgsz",    type=int,   default=300)
    p.add_argument("--batch",    type=int,   default=32)
    p.add_argument("--lr",       type=float, default=1e-3)
    p.add_argument("--patience", type=int,   default=10)
    p.add_argument("--output",   default="models")
    train(p.parse_args())
