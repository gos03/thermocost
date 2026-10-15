# Guide de Déploiement - Thermocost3 sur OVH

## Architecture

- **Application**: FastAPI + Uvicorn (containerisée)
- **Hébergement**: Serveur Debian sur OVH
- **Orchestration**: Docker Compose
- **Proxy Web**: Nginx (optionnel)
- **CI/CD**: GitHub Actions

## Étape 1: Configuration du serveur OVH

### 1.1 Préparation initiale

```bash
# Sur votre serveur OVH
curl -O https://raw.githubusercontent.com/gos03/thermocost3/main/deploy/setup-ovh.sh
chmod +x setup-ovh.sh
./setup-ovh.sh
```

Ce script installera:
- Docker
- Docker Compose
- Git et utilitaires nécessaires
- Créera l'utilisateur `deployer`

### 1.2 Clonage du repository

```bash
# Sur le serveur
cd /opt/thermocost3
git clone https://github.com/gos03/thermocost3.git .
```

## Étape 2: Configuration des secrets GitHub

Dans les paramètres du repository GitHub (`Settings > Secrets and variables > Actions`), ajouter:

- **OVH_SSH_KEY**: Votre clé SSH privée (générer avec `ssh-keygen -t ed25519`)
- **OVH_HOST**: Adresse IP ou domaine du serveur (ex: `123.45.67.89`)
- **OVH_USER**: Utilisateur SSH (ex: `deployer` ou votre utilisateur)

### Générer une clé SSH dédiée au déploiement:

```bash
# Sur votre machine locale
ssh-keygen -t ed25519 -f ~/.ssh/thermocost3_deploy -C "thermocost3-deploy"

# Afficher la clé publique
cat ~/.ssh/thermocost3_deploy.pub

# Ajouter la clé publique au serveur
ssh-copy-id -i ~/.ssh/thermocost3_deploy.pub deployer@OVH_HOST
```

## Étape 3: Configuration du serveur

### 3.1 Préparation du répertoire d'application

```bash
# Sur le serveur
cd /opt/thermocost3

# Créer un fichier .env si nécessaire
touch .env

# Démarrage initial
docker compose up -d
```

### 3.2 Configuration d'Nginx (optionnel mais recommandé)

```bash
# Sur le serveur
sudo cp deploy/nginx.conf /etc/nginx/sites-available/thermocost3
sudo ln -s /etc/nginx/sites-available/thermocost3 /etc/nginx/sites-enabled/thermocost3

# Tester la configuration
sudo nginx -t

# Redémarrer Nginx
sudo systemctl restart nginx
```

### 3.3 SSL avec Let's Encrypt (optionnel)

```bash
# Installer Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Générer un certificat
sudo certbot certonly --nginx -d votre-domaine.com

# Mettre à jour nginx.conf avec les chemins SSL
```

## Étape 4: Déploiement Automatique

Une fois les secrets GitHub configurés, le déploiement se fait automatiquement:

1. **Push sur la branche `main`**
   ```bash
   git push origin main
   ```

2. **GitHub Actions va**:
   - Construire l'image Docker
   - L'envoyer au serveur via SSH
   - Redémarrer le container avec la nouvelle image

3. **Vérifier le déploiement**:
   ```bash
   # Sur le serveur
   docker compose logs -f
   
   # Vérifier la santé
   curl http://localhost:8000/
   ```

## Commandes utiles

### Sur le serveur

```bash
# Voir les containers en cours
docker ps

# Voir les logs
docker compose logs -f thermocost

# Redémarrer l'application
docker compose restart

# Arrêter l'application
docker compose down

# Reconstruire l'image
docker compose build --no-cache

# Mettre à jour le code et redémarrer
cd /opt/thermocost3
git pull origin main
docker compose up -d
```

### Monitoring

```bash
# Vérifier l'état de l'application
curl http://localhost:8000/

# Voir l'utilisation des ressources
docker stats

# Voir les événements Docker
docker events
```

## Troubleshooting

### Port 8000 déjà utilisé
```bash
# Trouver le processus
sudo lsof -i :8000

# Tuer le processus ou modifier le port dans docker-compose.yml
```

### Permission denied pour Docker
```bash
# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker
```

### Container qui crash au démarrage
```bash
# Voir les logs détaillés
docker compose logs thermocost

# Déboguer dans le container
docker compose run --rm thermocost /bin/bash
```

### Problèmes de connexion SSH
```bash
# Tester la connexion
ssh -i ~/.ssh/thermocost3_deploy deployer@OVH_HOST

# Vérifier les logs de sshd
sudo tail -f /var/log/auth.log
```

## Sauvegarde et Maintenance

### Sauvegarde des données

```bash
# Si vous avez des volumes Docker
docker volume ls
docker volume inspect nom-du-volume
```

### Mise à jour de l'application

```bash
# Sur votre machine locale
git pull origin main
# Faire les modifications nécessaires
git push origin main
# Le déploiement se fait automatiquement via GitHub Actions
```

## Sécurité

- ✅ Clés SSH dédiées au déploiement
- ✅ Utilisateur non-root pour Docker
- ✅ HTTPS recommandé (Let's Encrypt)
- ✅ Firewall: Ouvrir seulement les ports nécessaires (80, 443)
- ✅ Mettre à jour régulièrement le système: `sudo apt-get update && sudo apt-get upgrade`

## Support

Pour plus d'informations:
- Docker: https://docs.docker.com/
- GitHub Actions: https://docs.github.com/en/actions
- OVH: https://www.ovh.com/fr/
