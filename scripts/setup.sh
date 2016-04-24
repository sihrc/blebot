#!/bin/bash
sudo apt-get update
sudo apt-get install -y git
sudo apt-get install -y apt-transport-https ca-certificates
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
sudo mkdir -p /etc/apt/sources.list.d/
sudo echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" | sudo tee -a /etc/apt/sources.list.d/docker.list
sudo apt-get update && sudo apt-get purge lxc-docker && sudo apt-cache policy docker-engine

sudo apt-get install -y linux-image-extra-$(uname -r)
sudo apt-get install -y apparmor docker-engine
sudo service docker start

chmod og+X /root
sudo apt-get install -y build-essential postgresql postgresql-contrib
sudo service postgresql start
sudo -u postgres createuser -s blebot
sudo -u postgres psql -c "ALTER USER blebot WITH PASSWORD 'blerocks';"
sed -i -e "s/#listen_addresses = 'localhost'/listen_addresses = '172.17.0.0/16'/g" /etc/postgresql/9.3/main/postgresql.conf
# Setup Script
mkdir ~/blebot && cd ~/blebot && git init

git config --global user.name "Chris Lee"
git config --global user.email "sihrc.c.lee@gmail.com"

./scripts/deploy.sh
