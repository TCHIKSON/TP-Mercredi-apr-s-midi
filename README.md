# TP - API REST devant un LLM local (Ollama)

Mini API REST en HTTP pur (aucun framework, uniquement la stdlib Python) qui
expose un modele LLM installe localement via [Ollama](https://ollama.com/).

## Prerequis

- [Ollama](https://ollama.com/) installe et lance (tourne en local sur `http://localhost:11434`)
- Un modele pull, par exemple :

  ```bash
  ollama pull gemma3:4b
  ```

- Python 3.9+ (aucune dependance externe a installer)

Verifier qu'Ollama fonctionne et que le modele est bien present :

```bash
ollama list
curl http://localhost:11434/api/version
```

## Lancer l'API

```bash
python server.py
```

Le serveur demarre sur `http://localhost:8080`.

Si un autre modele que `gemma3:4b` est utilise, modifier la constante
`OLLAMA_MODEL` en haut de [server.py](server.py).

## Endpoint

### `GET /ask?question=<texte>`

- **Parametre** : `question` (obligatoire, texte de la question, url-encode)
- **Reponse succes** : `200 OK`, `Content-Type: text/plain; charset=utf-8`,
  corps = reponse brute du modele
- **Erreurs** :
  - `400` : parametre `question` manquant ou vide
  - `404` : route inconnue (autre chemin que `/ask`)
  - `502` : Ollama injoignable (verifier qu'il tourne sur le port 11434)
  - `504` : timeout, le modele a mis trop de temps a repondre

## Exemples d'appel

### curl

```bash
curl "http://localhost:8080/ask?question=Dis%20bonjour%20en%20une%20phrase"
```

```bash
curl -G "http://localhost:8080/ask" --data-urlencode "question=Combien font 2+2 ?"
```

### Postman

- Methode : `GET`
- URL : `http://localhost:8080/ask`
- Params : `question` = `Dis bonjour en une phrase`

## Notes

- Aucune dependance externe : le serveur repose uniquement sur `http.server`
  et `urllib` (stdlib Python).
- Encodage : la requete envoyee a Ollama et la reponse HTTP renvoyee au
  client sont explicitement encodees/decodees en UTF-8 pour eviter les
  problemes d'accents.
- Le serveur est threade (`ThreadingHTTPServer`) : plusieurs requetes
  peuvent etre traitees en parallele.
- Fonctionne entierement en local : pas besoin de ngrok tant que la machine
  est assez performante pour faire tourner le modele.
