from pathlib import Path

import gradio as gr
import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader

from dataset import load_datasets
from model import CLASS_NAMES, FashionCNN

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CHECKPOINT_PATH = Path(__file__).parent / "checkpoints" / "fashion_cnn.pt"

model = FashionCNN().to(DEVICE)
model_ready = False

if CHECKPOINT_PATH.exists():
    model.load_state_dict(torch.load(CHECKPOINT_PATH, map_location=DEVICE))
    model.eval()
    model_ready = True


def train(epochs, batch_size, lr, progress=gr.Progress()):
    """Entraine le modele sur Fashion-MNIST et yield l'etat courant pour l'UI."""
    global model_ready

    model_ready = False
    epochs, batch_size = int(epochs), int(batch_size)

    yield (
        "Chargement du dataset...",
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
    )

    train_ds, test_ds = load_datasets()
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=256)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = torch.nn.CrossEntropyLoss()

    model.train()
    for epoch in range(1, epochs + 1):
        running_loss, correct, total = 0.0, 0, 0
        for step, (images, labels) in enumerate(train_loader):
            images, labels = images.to(DEVICE), labels.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            correct += (outputs.argmax(1) == labels).sum().item()
            total += labels.size(0)

            progress(
                (epoch - 1 + step / len(train_loader)) / epochs,
                desc=f"Epoque {epoch}/{epochs}",
            )

        yield (
            f"Epoque {epoch}/{epochs} - loss: {running_loss / total:.4f} - "
            f"accuracy entrainement: {correct / total:.2%}",
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False),
        )

    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = model(images)
            correct += (outputs.argmax(1) == labels).sum().item()
            total += labels.size(0)
    test_acc = correct / total

    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), CHECKPOINT_PATH)
    model_ready = True

    yield (
        f"Entrainement termine ! Precision sur le jeu de test : {test_acc:.2%}",
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(interactive=True),
    )


def _preprocess(image: Image.Image) -> np.ndarray:
    img = image.convert("L").resize((28, 28), Image.Resampling.LANCZOS)
    array = np.array(img, dtype=np.float32)

    # Fashion-MNIST : fond noir, vetement clair. Une photo deposee a en general
    # la polarite inverse (fond clair, vetement plus fonce) : si le pourtour de
    # l'image est plus clair que le centre, on inverse pour matcher le dataset.
    border = np.concatenate([array[0, :], array[-1, :], array[:, 0], array[:, -1]])
    center = array[8:20, 8:20]
    if border.mean() > center.mean():
        array = 255.0 - array

    return array / 255.0


def predict(image):
    if not model_ready:
        return "Le modele n'est pas encore entraine."
    if image is None:
        return "Veuillez deposer une image."

    array = _preprocess(image)
    tensor = torch.from_numpy(array).unsqueeze(0).unsqueeze(0).to(DEVICE)

    model.eval()
    with torch.no_grad():
        probs = torch.softmax(model(tensor), dim=1)[0]
        pred_idx = int(probs.argmax())

    return f"{CLASS_NAMES[pred_idx]} ({probs[pred_idx]:.1%} de confiance)"


with gr.Blocks(title="Fashion-MNIST Classifier") as demo:
    gr.Markdown("# Classification d'accessoires de mode (Fashion-MNIST + PyTorch)")
    gr.Markdown(
        "1. Cliquez sur **Entrainer** pour entrainer le modele sur Fashion-MNIST.\n"
        "2. Une fois l'entrainement termine, deposez une image d'accessoire de mode.\n"
        "3. Cliquez sur **Detecter** pour obtenir la prediction."
    )

    with gr.Row():
        epochs_input = gr.Slider(1, 10, value=3, step=1, label="Epoques")
        batch_size_input = gr.Slider(32, 256, value=128, step=32, label="Batch size")
        lr_input = gr.Number(value=1e-3, label="Learning rate")

    train_btn = gr.Button("Entrainer", variant="primary")
    status = gr.Textbox(
        label="Statut de l'entrainement",
        interactive=False,
        value=(
            "Modele deja entraine (checkpoint charge), pret pour la prediction."
            if model_ready
            else "Modele non entraine. Cliquez sur Entrainer."
        ),
    )

    gr.Markdown(
        "**Pour de meilleurs resultats** : photographiez un seul vetement/accessoire, "
        "bien centre, remplissant la majorite du cadre, sur un fond uni si possible."
    )

    with gr.Row():
        image_input = gr.Image(type="pil", label="Image a classifier", interactive=model_ready)
        result_output = gr.Textbox(label="Resultat", interactive=False)

    detect_btn = gr.Button("Detecter", interactive=model_ready)

    train_btn.click(
        fn=train,
        inputs=[epochs_input, batch_size_input, lr_input],
        outputs=[status, train_btn, image_input, detect_btn],
    )

    detect_btn.click(fn=predict, inputs=image_input, outputs=result_output)


if __name__ == "__main__":
    demo.launch()
