# TP - Classification Fashion-MNIST avec PyTorch + Gradio

Modele maison (CNN PyTorch) entraine sur le dataset [Fashion-MNIST](https://github.com/zalandoresearch/fashion-mnist)
de Zalando pour classifier des images d'accessoires de mode (28x28px, niveaux de
gris) parmi 10 categories. Une interface [Gradio](https://www.gradio.app/) permet
de lancer l'entrainement, deposer une image, puis lancer une prediction.

- **IN** : une image d'accessoire de mode
- **OUT** : l'estimation la plus probable parmi les 10 categories (ex. `Bag`)

## Prerequis

- Python 3.9 a 3.12 (Gradio n'est pas garanti sur les toutes dernieres versions
  de Python)
- Les dependances du fichier [requirements.txt](requirements.txt)
- Le dataset Fashion-MNIST, deja present dans [MNIST-dataset/](MNIST-dataset/)
  (fichiers `train-images-idx3-ubyte`, `train-labels-idx1-ubyte`,
  `t10k-images-idx3-ubyte`, `t10k-labels-idx1-ubyte`)

## Installation

```bash
cd MNIST-Fashion+torch
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

### Structure du projet

```
MNIST-Fashion+torch/
├── MNIST-dataset/     # dataset Fashion-MNIST (format idx-ubyte + CSV)
├── model.py           # architecture du CNN (FashionCNN) + noms des classes
├── dataset.py          # lecture des fichiers idx-ubyte -> Dataset PyTorch
├── app.py              # interface Gradio (entrainement + prediction)
├── requirements.txt
└── checkpoints/         # cree apres entrainement, non versionne (fashion_cnn.pt)
```

## Utilisation

```bash
python app.py
```

Gradio demarre un serveur local (par defaut `http://127.0.0.1:7860`) et ouvre
l'interface dans le navigateur.

### Dans l'interface

1. **Entrainer** : lance l'entrainement du CNN sur les 60 000 images
   d'entrainement (nombre d'epoques et batch size reglables). Une barre de
   progression et un texte de statut indiquent que le calcul est en cours ;
   ils s'arretent quand l'entrainement est termine. Le modele est ensuite
   evalue sur les 10 000 images de test et sauvegarde dans
   `checkpoints/fashion_cnn.pt`.
2. Une fois l'entrainement termine, le champ de depot d'image et le bouton
   **Detecter** deviennent cliquables. Deposez une image (elle s'affiche
   immediatement).
3. **Detecter** : lance une prediction sur l'image deposee et affiche le
   resultat (ex. `Bag (94.3% de confiance)`).

Si `checkpoints/fashion_cnn.pt` existe deja (entrainement precedent), il est
charge automatiquement au demarrage et la prediction est utilisable sans
re-entrainer.

### Conseils pour de meilleures predictions

Le modele est entraine sur des images produit propres : fond noir uni,
vetement seul, bien centre. Deux ecarts frequents avec une photo prise au
telephone degradent fortement la prediction :

- **Polarite des couleurs** : Fashion-MNIST a un fond noir et un vetement
  clair, l'inverse d'une photo classique (fond clair, vetement plus fonce).
  `app.py` detecte automatiquement ce cas (comparaison bord/centre de
  l'image) et inverse les couleurs si besoin.
- **Cadrage** : un fond charge, un vetement pas centre ou qui ne remplit pas
  le cadre restent un ecart important par rapport aux donnees d'entrainement
  (le modele n'a jamais vu de fond de piece, de main, etc.). Pour de
  meilleurs resultats, photographiez le vetement seul, centre, sur un fond
  uni si possible.

### Classes

`T-shirt/top`, `Trouser`, `Pullover`, `Dress`, `Coat`, `Sandal`, `Shirt`,
`Sneaker`, `Bag`, `Ankle boot`.

### Notes

- Le modele est un petit CNN (2 blocs conv+pool, puis 2 couches denses),
  suffisant pour depasser ~90% de precision en quelques epoques sur CPU.
- `venv/` et `checkpoints/` ne sont pas versionnes (voir le `.gitignore` a la
  racine du repo). Le dataset volumineux (`MNIST-dataset/`) non plus : les
  CSV depassent la limite de 100 Mo de GitHub.
