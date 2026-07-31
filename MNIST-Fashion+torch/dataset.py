import struct
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset

DATA_DIR = Path(__file__).parent / "MNIST-dataset"


def _load_idx_images(path: Path) -> np.ndarray:
    with open(path, "rb") as f:
        _, num, rows, cols = struct.unpack(">IIII", f.read(16))
        data = np.frombuffer(f.read(), dtype=np.uint8).copy()
    return data.reshape(num, rows, cols)


def _load_idx_labels(path: Path) -> np.ndarray:
    with open(path, "rb") as f:
        _, num = struct.unpack(">II", f.read(8))
        return np.frombuffer(f.read(), dtype=np.uint8).copy()


class FashionMNISTDataset(Dataset):
    """Wrappe les images/labels Fashion-MNIST (format idx-ubyte) en dataset PyTorch."""

    def __init__(self, images: np.ndarray, labels: np.ndarray):
        self.images = torch.from_numpy(images).float().unsqueeze(1) / 255.0  # N,1,28,28
        self.labels = torch.from_numpy(labels).long()

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx):
        return self.images[idx], self.labels[idx]


def load_datasets() -> tuple[FashionMNISTDataset, FashionMNISTDataset]:
    """Charge les jeux d'entrainement et de test depuis MNIST-dataset/."""
    train_images = _load_idx_images(DATA_DIR / "train-images-idx3-ubyte")
    train_labels = _load_idx_labels(DATA_DIR / "train-labels-idx1-ubyte")
    test_images = _load_idx_images(DATA_DIR / "t10k-images-idx3-ubyte")
    test_labels = _load_idx_labels(DATA_DIR / "t10k-labels-idx1-ubyte")

    return (
        FashionMNISTDataset(train_images, train_labels),
        FashionMNISTDataset(test_images, test_labels),
    )
