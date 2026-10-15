#!/bin/bash
# Post-deployment script to be run on the OVH server
# Usage: bash post-deploy.sh

set -e

echo "================================"
echo "Post-deployment configuration"
echo "================================"

# Create systemd service
echo "Configuring systemd service..."
sudo cp thermocost3.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable thermocost3.service

# Optional: Install and configure Nginx
read -p "Do you want to install and configure Nginx? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing Nginx..."
    sudo apt-get install -y nginx
    sudo cp nginx.conf /etc/nginx/sites-available/thermocost3
    sudo ln -sf /etc/nginx/sites-available/thermocost3 /etc/nginx/sites-enabled/thermocost3
    sudo nginx -t
    sudo systemctl enable nginx
    sudo systemctl restart nginx
    echo "✅ Nginx configured"
fi

# Optional: Install Let's Encrypt SSL
read -p "Do you want to set up Let's Encrypt SSL? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your domain: " domain
    echo "Installing Certbot..."
    sudo apt-get install -y certbot python3-certbot-nginx
    sudo certbot certonly --nginx -d "$domain"
    echo "✅ SSL certificate obtained. Update nginx.conf with SSL paths."
fi

echo ""
echo "================================"
echo "Setup complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Start the service: sudo systemctl start thermocost3"
echo "2. Check status: sudo systemctl status thermocost3"
echo "3. View logs: sudo journalctl -u thermocost3 -f"
