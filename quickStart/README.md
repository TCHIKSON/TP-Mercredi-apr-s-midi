# TP - Quickstart Django REST Framework

Reproduction du tutoriel officiel [Django REST Framework - Quickstart](https://www.django-rest-framework.org/tutorial/quickstart/) :
une API REST qui expose les modeles `User` et `Group` de Django (auth builtin)
via des `ModelViewSet` et un routeur automatique.

## Installation

Prerequis : Python 3.9+ et les dependances du fichier [requirements.txt](requirements.txt).

```bash
cd quickStart
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

### Structure du projet

```
quickStart/
├── manage.py
├── requirements.txt
├── db.sqlite3              # cree par migrate, non versionne
└── tutorial/                # projet Django
    ├── settings.py          # INSTALLED_APPS + REST_FRAMEWORK
    ├── urls.py               # router DRF + api-auth
    └── quickstart/           # app
        ├── serializers.py    # UserSerializer, GroupSerializer
        └── views.py          # UserViewSet, GroupViewSet
```

### Preparer la base de donnees

```bash
python manage.py migrate
python manage.py createsuperuser
```

Un superuser `admin` / `admin` existe deja en local pour tester rapidement
(base `db.sqlite3` non versionnee, a recreer si besoin avec les commandes
ci-dessus).

## Utilisation

### Lancer l'API

```bash
python manage.py runserver
```

Le serveur demarre sur `http://127.0.0.1:8000`.

### Endpoints

L'API est enregistree via un `DefaultRouter` DRF (routes CRUD automatiques) :

- `GET/POST /users/` et `GET/PUT/PATCH/DELETE /users/<id>/`
- `GET/POST /groups/` et `GET/PUT/PATCH/DELETE /groups/<id>/`

Acces protege par `IsAuthenticated` : authentification requise (session ou
basic auth). `api-auth/` expose les vues de connexion/deconnexion pour
l'API navigable (browsable API).

### Exemples d'appel

**cURL**

```bash
curl -u admin -H 'Accept: application/json; indent=4' http://127.0.0.1:8000/users/
```

**Navigateur (API navigable DRF)**

Ouvrir `http://127.0.0.1:8000/users/` dans un navigateur : DRF affiche une
interface HTML permettant de parcourir et tester l'API (formulaires inclus),
avec un lien de connexion en haut a droite (`api-auth/`).

**Postman**

- Methode : `GET`
- URL : `http://127.0.0.1:8000/users/`
- Onglet **Authorization** > `Basic Auth` > utilisateur/mot de passe du
  superuser

### Notes

- `DEFAULT_PAGINATION_CLASS` est fixe a `PageNumberPagination` avec
  `PAGE_SIZE = 10` (voir `tutorial/settings.py`).
- `venv/`, `db.sqlite3` et les fichiers `*.log` ne sont pas versionnes, voir
  le `.gitignore` a la racine du repo.
- Les serializers utilisent `HyperlinkedModelSerializer` : les relations
  (ex. `groups` sur `User`) sont representees par des URLs plutot que des
  ID bruts.
