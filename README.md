

# Resume Skill Extractor & Matcher

Ce projet est une API Flask qui permet d'extraire des compétences à partir d’un CV sous forme d’image (PNG, JPG, JPEG), et de les faire correspondre avec une base de données d’offres d’emploi stockées dans MongoDB.

## Fonctionnalités

- Extraction automatique de texte depuis un CV au format image via OCR.
- Extraction de compétences à partir du texte extrait.
- Correspondance des compétences extraites avec les offres d'emploi existantes.
- Interface web simple pour tester l’upload.
- Endpoints API accessibles via Postman ou d'autres clients.

## Types de fichiers supportés

Seuls les fichiers image sont acceptés :

- **.png**
- **.jpg**
- **.jpeg**

**Les fichiers PDF ou Word ne sont pas pris en charge pour le moment.**

## Architecture

```plaintext
+-------------------+
|   CV Image (.jpg) |
+-------------------+
         |
         v
+-------------------------+
| OCR (EasyOCR)          |
| Extraction de texte    |
+-------------------------+
         |
         v
+-----------------------------+
| SkillExtractor             |
| Extraction des compétences |
+-----------------------------+
         |
         v
+-----------------------------+
| SkillMatcher                |
| Correspondance avec offres |
+-----------------------------+
```

## Prérequis

- Python 3.9+
- MongoDB Atlas (base de données cloud)
- Environnement virtuel (recommandé)

## Installation

1. **Cloner le projet**

```bash
git clone https://github.com/AMIRIkarima/skill_extractor_api.git
cd skill-matcher-api
```

2. **Créer un environnement virtuel**

```bash
python -m venv venv
sur Windows : venv\Scripts\activate
```

3. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

4. **Configurer les variables d’environnement**

Créer un fichier `.env` à la racine et ajouter :

```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/
```

Assurez-vous que votre IP est bien autorisée dans MongoDB Atlas.

## Lancer le serveur

```bash
python app.py
```

## Tester via l’interface Web

Ouvrir dans un navigateur :

```
http://localhost:5000/
```

## Tester avec Postman

###  Extraire des compétences

- **Méthode** : POST
- **URL** : `/process`
- **Body** : `form-data`
  - `file` : sélectionner une image de CV


## Organisation du code

- `app.py` : Point d’entrée principal.
- `skill_extractor.py` : Traitement OCR et extraction des compétences.
- `job_matcher.py` : Chargement des offres depuis MongoDB et matching.

