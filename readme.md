# Thermocost – FastAPI

Application de calcul de coûts thermiques avec interface web basée sur FastAPI.

## Démarrage Local

### Avec Python (développement)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

L'application sera accessible à `http://localhost:8000`

### Avec Docker (recommandé)

```bash
# Construire l'image
docker build -t thermocost .

# Lancer le container
docker run -d -p 8000:8000 --name thermocost thermocost
```

### Avec Docker Compose

```bash
# Démarrer l'application
docker compose up -d

# Voir les logs
docker compose logs -f thermocost

# Arrêter l'application
docker compose down
```

## Déploiement en Production

Pour déployer sur un serveur OVH sous Debian, voir le guide complet: [deploy/DEPLOYMENT.md](deploy/DEPLOYMENT.md)

### Résumé du processus:

1. **Configuration du serveur**:
   ```bash
   curl -O https://raw.githubusercontent.com/gos03/thermocost3/main/deploy/setup-ovh.sh
   chmod +x setup-ovh.sh
   ./setup-ovh.sh
   ```

2. **Configuration des secrets GitHub**:
   - `OVH_SSH_KEY`: Clé SSH privée
   - `OVH_HOST`: Adresse IP du serveur
   - `OVH_USER`: Utilisateur SSH (ex: deployer)

3. **Déploiement automatique**:
   ```bash
   git push origin main  # Le déploiement se fait automatiquement via GitHub Actions
   ```

## Architecture

- **Application**: FastAPI + Uvicorn
- **Containerisation**: Docker
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions
- **Proxy**: Nginx (optionnel)
- **Hébergement**: Serveur Debian sur OVH
