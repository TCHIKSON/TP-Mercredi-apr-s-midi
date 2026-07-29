# TP - API REST pour la detection d'objets avec YOLO

Mini API REST construite avec [FastAPI](https://fastapi.tiangolo.com/) qui
expose un modele [YOLO](https://docs.ultralytics.com/) (via la librairie
[Ultralytics](https://github.com/ultralytics/ultralytics)) pour detecter des
objets sur une image envoyee en POST. L'API peut repondre soit avec les
annotations au format JSON, soit avec l'image annotee (boites + labels).

## Prerequis

- Python 3.9+
- Les dependances du fichier [requirements.txt](requirements.txt)

## Installation

```bash
cd yolo
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

Le modele `yolov8n.pt` (le plus leger de la famille YOLOv8) est telecharge
automatiquement par Ultralytics au premier lancement de l'API.

## Lancer l'API

```bash
python main.py
```

ou avec uvicorn directement (rechargement automatique en dev) :

```bash
uvicorn main:app --reload --port 8000
```

Le serveur demarre sur `http://localhost:8000`.
La documentation interactive Swagger est disponible sur
`http://localhost:8000/docs`.

## Exposer l'API sur Internet avec ngrok (optionnel)

Par defaut l'API tourne uniquement en local (`localhost:8000`), suffisant
pour Postman/cURL sur la meme machine. Pour la rendre joignable depuis
l'exterieur (autre poste, telephone, service externe), un tunnel
[ngrok](https://ngrok.com/) peut etre demarre automatiquement au lancement.

1. Creer un compte gratuit sur [ngrok.com](https://ngrok.com/) et recuperer
   son authtoken.
2. Configurer l'authtoken une seule fois :

   ```bash
   python -m pyngrok authtoken <VOTRE_TOKEN>
   ```

3. Lancer l'API avec le tunnel active :

   ```bash
   # Windows PowerShell
   $env:USE_NGROK="true"; python main.py

   # bash / macOS / Linux
   USE_NGROK=true python main.py
   ```

L'URL publique ngrok (ex: `https://xxxx.ngrok-free.app`) s'affiche dans la
console au demarrage : l'utiliser a la place de `http://localhost:8000` dans
Postman ou cURL pour appeler l'API depuis l'exterieur.

## Endpoints

### `POST /detect`

- **Body** : `multipart/form-data`, champ `file` = image (jpg/png...)
- **Reponse** : `200 OK`, JSON avec la liste des objets detectes

```json
{
  "count": 2,
  "detections": [
    {
      "class_id": 0,
      "class_name": "person",
      "confidence": 0.91,
      "bbox": [34.2, 12.5, 210.8, 400.1]
    }
  ]
}
```

### `POST /detect/image`

- **Body** : `multipart/form-data`, champ `file` = image (jpg/png...)
- **Reponse** : `200 OK`, `Content-Type: image/jpeg`, l'image avec les boites
  et labels dessines dessus

## Exemples d'appel

### cURL

```bash
curl -X POST "http://localhost:8000/detect" \
  -F "file=@chemin/vers/mon_image.jpg"
```

```bash
curl -X POST "http://localhost:8000/detect/image" \
  -F "file=@chemin/vers/mon_image.jpg" \
  --output resultat_annote.jpg
```

### Postman

- Methode : `POST`
- URL : `http://localhost:8000/detect` (ou `/detect/image`)
- Onglet **Body** > `form-data`
- Cle : `file`, type `File`, valeur : selectionner une image sur le disque
- Envoyer : le JSON (ou l'image annotee) est renvoye dans la reponse

## Notes

- Le modele est charge une seule fois au demarrage de l'API (variable
  globale `model` dans [main.py](main.py)) pour eviter de le recharger a
  chaque requete.
- `yolov8n.pt` et le dossier `runs/` (genere par Ultralytics) ne sont pas
  versionnes, voir le `.gitignore` a la racine du repo.
- ngrok est optionnel (voir section dediee ci-dessus) : uniquement utile
  pour exposer l'API en dehors de la machine locale.
