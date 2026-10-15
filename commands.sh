#!/bin/bash
# Makefile-like commands for common tasks
# Usage: bash commands.sh <command>

set -e

COMMAND=${1:-help}

case $COMMAND in
  help)
    echo "Thermocost3 - Commandes utiles"
    echo ""
    echo "Usage: bash commands.sh <command>"
    echo ""
    echo "Commands locales:"
    echo "  dev-run        Lancer en mode développement avec hot-reload"
    echo "  dev-build      Construire l'image Docker localement"
    echo "  dev-up         Démarrer avec Docker Compose"
    echo "  dev-down       Arrêter les containers Docker"
    echo "  dev-logs       Voir les logs en temps réel"
    echo ""
    echo "Serveur OVH:"
    echo "  server-setup   Installer Docker et dépendances sur OVH"
    echo "  server-deploy  Déployer vers le serveur OVH via SSH"
    echo "  server-logs    Voir les logs du serveur"
    echo ""
    echo "GitHub:"
    echo "  gh-secrets     Montrer comment configurer les secrets GitHub"
    ;;
  
  dev-run)
    echo "🚀 Démarrage en mode développement..."
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload
    ;;
  
  dev-build)
    echo "🔨 Construction de l'image Docker..."
    docker build -t thermocost:latest .
    ;;
  
  dev-up)
    echo "🐳 Démarrage avec Docker Compose..."
    docker compose up -d
    echo "✅ Application disponible sur http://localhost:8000"
    ;;
  
  dev-down)
    echo "🛑 Arrêt des containers..."
    docker compose down
    ;;
  
  dev-logs)
    echo "📋 Logs en temps réel..."
    docker compose logs -f thermocost
    ;;
  
  server-setup)
    echo "🖥️  Configuration du serveur OVH..."
    echo "Cette commande doit être exécutée sur votre serveur OVH:"
    echo ""
    echo "ssh deployer@votre-serveur"
    echo "curl -O https://raw.githubusercontent.com/gos03/thermocost3/main/deploy/setup-ovh.sh"
    echo "chmod +x setup-ovh.sh"
    echo "./setup-ovh.sh"
    ;;
  
  server-deploy)
    echo "📤 Déploiement vers OVH..."
    echo "Assurez-vous que les secrets GitHub sont configurés:"
    echo "  - OVH_SSH_KEY"
    echo "  - OVH_HOST"
    echo "  - OVH_USER"
    echo ""
    echo "Puis lancez:"
    echo "  git push origin main"
    ;;
  
  server-logs)
    echo "📋 Accès aux logs du serveur..."
    read -p "Entrez l'hôte OVH: " host
    read -p "Entrez l'utilisateur SSH: " user
    ssh "${user}@${host}" "cd /opt/thermocost3 && docker compose logs -f"
    ;;
  
  gh-secrets)
    echo "🔐 Configuration des secrets GitHub"
    echo ""
    echo "1. Générer une clé SSH dédiée:"
    echo "   ssh-keygen -t ed25519 -f ~/.ssh/thermocost3_deploy -C 'thermocost3-deploy'"
    echo ""
    echo "2. Copier la clé publique au serveur:"
    echo "   ssh-copy-id -i ~/.ssh/thermocost3_deploy.pub deployer@OVH_HOST"
    echo ""
    echo "3. Ajouter les secrets dans GitHub (Settings > Secrets > New repository secret):"
    echo ""
    echo "   Name: OVH_SSH_KEY"
    echo "   Value: [Contenu de ~/.ssh/thermocost3_deploy]"
    echo ""
    echo "   Name: OVH_HOST"
    echo "   Value: [IP ou domaine du serveur]"
    echo ""
    echo "   Name: OVH_USER"
    echo "   Value: deployer"
    echo ""
    echo "4. Tester la connexion:"
    echo "   ssh -i ~/.ssh/thermocost3_deploy deployer@OVH_HOST 'docker --version'"
    ;;
  
  *)
    echo "❌ Commande inconnue: $COMMAND"
    echo "Tapez: bash commands.sh help"
    exit 1
    ;;
esac
