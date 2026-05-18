#!/usr/bin/env bash
set -euxo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates \
  conntrack \
  curl \
  git \
  gnupg \
  apt-transport-https

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

. /etc/os-release
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y --no-install-recommends docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable --now docker
usermod -aG docker ubuntu

if [ ! -f /swapfile ]; then
  fallocate -l 2G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

curl -fsSL -o /usr/local/bin/kubectl "https://dl.k8s.io/release/v1.34.0/bin/linux/amd64/kubectl"
chmod +x /usr/local/bin/kubectl

curl -fsSL -o /tmp/minikube.deb "https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb"
dpkg -i /tmp/minikube.deb

curl -fsSL -o /tmp/helm.tar.gz "https://get.helm.sh/helm-v4.2.0-linux-amd64.tar.gz"
tar -xzf /tmp/helm.tar.gz -C /tmp
install -m 0755 /tmp/linux-amd64/helm /usr/local/bin/helm

sudo -u ubuntu minikube start --driver=docker --cpus=2 --memory=1800mb
sudo -u ubuntu minikube addons enable ingress

cat >/etc/profile.d/minikube.sh <<'EOF'
alias k='kubectl'
EOF
