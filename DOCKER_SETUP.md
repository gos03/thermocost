# Configuration de Déploiement - Résumé

Voici ce qui a été configuré pour Thermocost3 :

## 📦 Fichiers Docker

✅ **Dockerfile**
- Image multi-stage optimisée (builder + runtime)
- Basée sur Python 3.12-slim
- Healthcheck intégré
- Prête pour production

✅ **.dockerignore**
- Exclut les fichiers inutiles du build
- Réduit la taille de l'image

✅ **docker-compose.yml**
- Service Thermocost configuré
- Port 8000 exposé
- Healthcheck Docker Compose
- Volume lecture-seule pour le code
- Redémarrage automatique

## 🚀 CI/CD - GitHub Actions

✅ **.github/workflows/deploy.yml**
- Build Docker automatique à chaque push sur main
- Envoi de l'image sur le serveur OVH via SSH
- Redémarrage automatique du container
- Multi-stage : build + deploy

**Secrets requis:**
- `OVH_SSH_KEY`: Clé SSH privée
- `OVH_HOST`: Adresse IP/domaine du serveur
- `OVH_USER`: Utilisateur SSH (deployer)

## 🖥️ Configuration Serveur OVH

✅ **deploy/setup-ovh.sh**
- Installation de Docker
- Installation de Docker Compose
- Créer l'utilisateur `deployer`
- Préparation du répertoire d'application

✅ **deploy/thermocost3.service**
- Service systemd pour gérer l'application
- Redémarrage automatique en cas de crash
- Démarrage au boot du serveur

✅ **deploy/post-deploy.sh**
- Configuration post-installation
- Installation optionnelle de Nginx
- Configuration optionnelle Let's Encrypt SSL

## 🌐 Web Server

✅ **deploy/nginx.conf**
- Configuration Nginx comme reverse proxy
- Redirection HTTP/HTTPS
- Support SSL Let's Encrypt

## 📚 Documentation

✅ **deploy/DEPLOYMENT.md**
- Guide complet de déploiement
- Instructions étape par étape
- Commandes utiles
- Troubleshooting

✅ **commands.sh**
- Commandes pratiques pour développement local
- Commandes pour serveur OVH
- Configuration des secrets GitHub

✅ **readme.md** (mis à jour)
- Instructions démarrage local
- Instructions Docker
- Lien vers guide déploiement

✅ **.env.example**
- Variables d'environnement de référence

## 🎯 Workflow de Déploiement

```
1. Développement local
   └─ bash commands.sh dev-up

2. Push sur GitHub
   └─ git push origin main

3. GitHub Actions
   ├─ Build Docker image
   ├─ SSH vers OVH
   ├─ Charger l'image
   ├─ Redémarrer le container
   └─ Nettoyer les anciennes images

4. Application en ligne
   └─ http://votre-domaine:8000
```

## ✅ Checklist de Configuration

- [ ] Générer une clé SSH dédiée: `ssh-keygen -t ed25519`
- [ ] Ajouter les secrets GitHub: OVH_SSH_KEY, OVH_HOST, OVH_USER
- [ ] Exécuter setup-ovh.sh sur le serveur
- [ ] Cloner le repo sur le serveur: `/opt/thermocost3`
- [ ] Tester la connexion SSH
- [ ] Premier push pour tester le déploiement automatique
- [ ] Vérifier les logs GitHub Actions
- [ ] Vérifier les logs du serveur

## 📝 Notes

- L'image Docker utilise un build multi-stage pour minimiser la taille
- Le container redémarre automatiquement en cas de crash
- Healthcheck intégré (vérifie que l'API répond)
- Nginx peut être configuré pour servir plusieurs domaines
- SSL Let's Encrypt est gratuit et automatisable

## 🆘 Support

Consultez les fichiers:
- **Déploiement**: `deploy/DEPLOYMENT.md`
- **Commandes**: `bash commands.sh help`
- **Logs GitHub**: Actions tab sur le repository
- **Logs Serveur**: `docker compose logs -f`
