import torch
from torchvision import transforms
from PIL import Image

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

def get_transforms(train=False, imgsz=300):
    if train:
        return transforms.Compose([
            transforms.Resize((int(imgsz * 1.07), int(imgsz * 1.07))),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.5),         
            transforms.RandomRotation(180),                 
            transforms.ColorJitter(
                brightness=0.2, contrast=0.2,
                saturation=0.1,                             
                hue=0.0                                  
            ),
            transforms.RandomResizedCrop(imgsz, scale=(0.8, 1.0)),  
            transforms.RandomAffine(
                degrees=0,                                 
                translate=(0.1, 0.1),                      
                scale=(0.9, 1.1)                           
            ),
            transforms.RandomPerspective(distortion_scale=0.2, p=0.3),  
            transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 1.0)),   
            transforms.RandomAutocontrast(p=0.3),
            transforms.RandomEqualize(p=0.2),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ])
    return transforms.Compose([
        transforms.Resize((imgsz, imgsz)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])

def preprocess_image(image: Image.Image) -> torch.Tensor:
    return get_transforms(False, 300)(image.convert("RGB")).unsqueeze(0)
