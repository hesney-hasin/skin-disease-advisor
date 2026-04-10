import torch
import torch.nn as nn
from torchvision import models
from PIL import Image
from typing import Tuple, List
from app.utils import preprocess_image
from app.schemas import PredictionItem

DISEASE_CLASSES = [
    "Eczema",
    "Warts, Molluscum & Viral Infections",
    "Melanoma",
    "Atopic Dermatitis",
    "Basal Cell Carcinoma (BCC)",
    "Melanocytic Nevi (NV)",
    "Benign Keratosis-like Lesions (BKL)",
    "Psoriasis & Lichen Planus",
    "Seborrheic Keratoses & Benign Tumors",
    "Tinea, Ringworm & Fungal Infections",
]

NUM_CLASSES = len(DISEASE_CLASSES)


def build_model(num_classes=NUM_CLASSES, freeze_backbone=False):
    model = models.efficientnet_b3(weights=models.EfficientNet_B3_Weights.IMAGENET1K_V1)
    if freeze_backbone:
        for p in model.features.parameters():
            p.requires_grad = False
    in_f = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_f, num_classes),
    )
    return model


class SkinDiseaseClassifier:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.is_loaded = False

    def load_model(self, path):
        self.model = build_model(NUM_CLASSES)
        try:
            self.model.load_state_dict(torch.load(path, map_location=self.device))
            print(f"Loaded weights from {path}")
        except FileNotFoundError:
            print(f"WARNING: {path} not found — using ImageNet backbone.")
        self.model.to(self.device).eval()
        self.is_loaded = True

    @torch.no_grad()
    def predict(self, image: Image.Image) -> Tuple[str, float, List[PredictionItem]]:
        tensor = preprocess_image(image).to(self.device)
        probs = torch.softmax(self.model(tensor), dim=1)[0]
        top5_vals, top5_idx = torch.topk(probs, 5)
        return (
            DISEASE_CLASSES[top5_idx[0].item()],
            top5_vals[0].item(),
            [
                PredictionItem(
                    disease=DISEASE_CLASSES[i.item()],
                    confidence=round(v.item(), 4),
                )
                for v, i in zip(top5_vals, top5_idx)
            ],
        )