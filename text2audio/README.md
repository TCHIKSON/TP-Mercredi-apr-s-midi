# TP III - text2audio (NeuTTS-2e + Django REST Framework + mini-frontend)

Mini API REST Django (avec Django REST Framework) qui genere de la parole a
partir de texte en executant le modele
[NeuTTS-2e](https://github.com/neuphonic/neutts) **en local** (package
[`neutts`](https://pypi.org/project/neutts/), PyTorch), sans dependre d'un
Space Hugging Face distant ni de token/quota. Un mini-frontend HTML/JS (servi
par Django) permet de tester l'API dans le navigateur avec un lecteur audio.

## Prerequis

- **Python 3.11 a 3.13** (voir "Pourquoi pas Python 3.14" ci-dessous)
- Les dependances du fichier [requirements.txt](requirements.txt) (PyTorch,
  transformers, neutts, neucodec... installation volumineuse, plusieurs
  centaines de Mo)
- Pas de compte ni de token necessaire : tout tourne en local

### Pourquoi pas Python 3.14

Ce TP a ete developpe sur une machine ou Python 3.14 est la version par
defaut, mais `pip install neutts` y echoue : `numpy` n'a pas encore de wheel
precompilee pour 3.14 et tente de se compiler depuis les sources, ce qui
echoue sans compilateur C/C++ installe (`Unknown compiler(s)`). Utiliser un
interpreteur Python 3.11/3.12/3.13 pour creer le venv resout le probleme :

```bash
py -3.13 -m venv venv          # si plusieurs Python sont installes (Windows)
# ou directement le chemin de l'interpreteur 3.13 si `python` pointe vers 3.14
```

## Installation

```bash
cd text2audio
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

## Lancer l'API

```bash
python manage.py runserver
```

Le serveur demarre sur `http://127.0.0.1:8000`.

- Mini-frontend : `http://127.0.0.1:8000/`
- Endpoint API : `http://127.0.0.1:8000/say/`

Le modele est charge en memoire au premier appel a `/say/` (variable globale
`_tts` dans [tts/views.py](tts/views.py), reutilisee ensuite pour toutes les
requetes). **Le tout premier appel telecharge les poids du modele** depuis
Hugging Face Hub (mis en cache localement) et peut prendre plusieurs minutes
selon la connexion et la machine (CPU) ; les appels suivants sont rapides.
Lors des tests, une phrase courte a pris environ 4 minutes au premier appel
(telechargement inclus).

## Endpoint

### `GET /say/?sentence=...&speaker=...&mood=...`

| Parametre  | Obligatoire | Valeurs possibles                                                          | Defaut    |
|------------|:-----------:|-----------------------------------------------------------------------------|-----------|
| `sentence` | oui         | texte libre (url-encode)                                                    | -         |
| `speaker`  | non         | `emily`, `paul`, `sophie`, `steven`                                         | `emily`   |
| `mood`     | non         | `neutral`, `angry`, `sad`, `happy`, `surprised`, `disgusted`, `fearful`     | `neutral` |

- **Reponse succes** : `200 OK`, `Content-Type: audio/wav`, corps = fichier
  WAV genere en local (mono, 16 bits, 24 kHz)
- **Erreurs** :
  - `400` : `sentence` manquant/vide, ou `speaker`/`mood` invalide (le corps
    de la reponse liste les valeurs acceptees)
  - `500` : erreur du modele NeuTTS-2e pendant l'inference

## Exemples d'appel

### cURL

```bash
curl -G "http://127.0.0.1:8000/say/" \
  --data-urlencode "sentence=Bonjour, ceci est un test" \
  --data-urlencode "speaker=emily" \
  --data-urlencode "mood=happy" \
  --output reponse.wav
```

### Navigateur

Ouvrir `http://127.0.0.1:8000/`, saisir une phrase, choisir une voix et une
emotion, cliquer sur "Generer l'audio" : le fichier WAV est recupere et joue
directement dans la page.

### Postman

- Methode : `GET`
- URL : `http://127.0.0.1:8000/say/`
- Params : `sentence`, `speaker`, `mood`
- La reponse binaire (WAV) peut etre ecoutee directement dans l'onglet
  "Body" de Postman (previsualisation audio)

## Notes

- `NeuTTS2E()` (voir [tts/views.py](tts/views.py)) expose 4 voix "pre-cuites"
  (`emily`, `paul`, `sophie`, `steven`) sans avoir besoin d'audio de
  reference, contrairement a `NeuTTS`/`NeuTTS-Nano` (clonage de voix a partir
  d'un echantillon audio, sans controle d'emotion). C'est ce qui permet
  l'API simple `tts.infer(sentence, speaker=..., emotion=...)`.
- Le WAV est construit en memoire avec `soundfile` (`io.BytesIO`) puis
  renvoye directement dans la reponse HTTP, sans fichier temporaire sur
  disque.
- `venv/`, `db.sqlite3` et `__pycache__/` ne sont pas versionnes, voir le
  `.gitignore` a la racine du repo ; les poids du modele sont mis en cache
  par `huggingface_hub` (hors de ce depot, generalement `~/.cache/huggingface`).
- Premiere approche testee : appeler le Space Hugging Face distant
  `neuphonic/neutts-2e` via `gradio_client`. Abandonnee au profit du modele
  local car le quota anonyme **ZeroGPU** du Space est tres restrictif
  (erreur immediate *"You have exceeded your ZeroGPU runs limit"* sans
  token), alors que l'inference locale ne depend d'aucun quota.
