#!/bin/bash
cd ~/blebot

git pull https://$GITHUB_ACCESS_TOKEN@github.com/sihrc/blebot.git

sudo docker kill $(sudo docker ps -q)
sudo docker build -t blebot .
sudo docker run -p 0.0.0.0:80:80 -e DISCORD_ACCESS_TOKEN=$DISCORD_ACCESS_TOKEN -v /var/lib/postgresql/9.3/main -d -t blebot
