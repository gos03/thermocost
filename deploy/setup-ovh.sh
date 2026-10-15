#!/bin/bash

# Setup script for OVH Debian server
# Run this once on your OVH server to set up the environment

set -e

echo "================================"
echo "Setting up Thermocost3 on OVH"
echo "================================"

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo "Installing Docker..."
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Enable Docker service
sudo systemctl enable docker
sudo systemctl start docker

# Add current user to docker group
sudo usermod -aG docker $USER

# Create application directory
echo "Creating application directory..."
sudo mkdir -p /opt/thermocost3
sudo chown $USER:$USER /opt/thermocost3

# Create deployment user (optional but recommended)
if ! id -u deployer &>/dev/null; then
    sudo useradd -m -s /bin/bash deployer
    sudo usermod -aG docker deployer
    sudo mkdir -p /home/deployer/.ssh
    sudo chown deployer:deployer /home/deployer/.ssh
    sudo chmod 700 /home/deployer/.ssh
    echo "Deployer user created. Add your public key to /home/deployer/.ssh/authorized_keys"
fi

# Install docker-compose standalone (if not already installed)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install additional utilities
echo "Installing utilities..."
sudo apt-get install -y git curl wget

# Verify installation
echo ""
echo "================================"
echo "Installation Summary"
echo "================================"
docker --version
docker compose version
echo "Application directory: /opt/thermocost3"
echo ""
echo "Setup complete! Next steps:"
echo "1. Clone the repository to /opt/thermocost3"
echo "2. Configure GitHub secrets (OVH_SSH_KEY, OVH_HOST, OVH_USER)"
echo "3. Push to main branch to trigger deployment"
echo ""
