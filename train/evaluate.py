import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from torch.utils.data import DataLoader, random_split
from torchvision import datasets
from app.model import build_model, DISEASE_CLASSES, NUM_CLASSES
from app.utils import get_transforms


def get_predictions(model, loader, device):
    all_preds, all_labels = [], []
    model.eval()
    with torch.no_grad():
        for imgs, labels in loader:
            preds = model(imgs.to(device)).argmax(1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())
    return np.array(all_preds), np.array(all_labels)


def evaluate(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Single ImageFolder — same transform (no augmentation) for both splits
    full_ds = datasets.ImageFolder(args.data_dir, transform=get_transforms(False, args.imgsz))
    total = len(full_ds)
    n_val = int(total * 0.15)

    # Reproduce EXACT same split as train.py using random_split
    train_split, val_split = random_split(
        full_ds, [total - n_val, n_val],
        generator=torch.Generator().manual_seed(42)
    )

    train_loader = DataLoader(train_split, batch_size=args.batch, shuffle=False, num_workers=2)
    val_loader   = DataLoader(val_split,   batch_size=args.batch, shuffle=False, num_workers=2)
    print(f"Train: {len(train_split):,} | Val/Test: {len(val_split):,}")

    model = build_model(NUM_CLASSES)
    model.load_state_dict(torch.load(args.weights, map_location=device))
    model.to(device)
    print(f"✓ Model loaded from {args.weights}\n")

    print("Evaluating train set...")
    train_preds, train_labels = get_predictions(model, train_loader, device)
    train_acc = accuracy_score(train_labels, train_preds)

    print("Evaluating val/test set...")
    val_preds, val_labels = get_predictions(model, val_loader, device)
    val_acc = accuracy_score(val_labels, val_preds)

    print(f"\n{'='*50}")
    print(f"  Train Accuracy : {train_acc:.4f}  ({train_acc*100:.2f}%)")
    print(f"  Val   Accuracy : {val_acc:.4f}  ({val_acc*100:.2f}%)")
    print(f"{'='*50}\n")

    print("--- Val/Test Set Classification Report ---")
    print(classification_report(val_labels, val_preds, target_names=DISEASE_CLASSES))

    cm = confusion_matrix(val_labels, val_preds)
    plt.figure(figsize=(14, 12))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=DISEASE_CLASSES, yticklabels=DISEASE_CLASSES)
    plt.title(f"Confusion Matrix — Val Accuracy: {val_acc:.2%}", fontsize=16)
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    out_path = os.path.join(os.path.dirname(args.weights), "confusion_matrix.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"✓ Confusion matrix saved → {out_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", default="data")
    p.add_argument("--weights",  default="models/efficientnet_skin.pth")
    p.add_argument("--imgsz",    type=int, default=300)
    p.add_argument("--batch",    type=int, default=32)
    evaluate(p.parse_args())
