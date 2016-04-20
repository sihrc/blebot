#!/bin/bash
cd ~/blebot

git pull https://$GITHUB_ACCESS_TOKEN@github.com/sihrc/blebot.git

NET_IF=`netstat -rn | awk '/^0.0.0.0/ {thif=substr($0,74,10); print thif;} /^default.*UG/ {thif=substr($0,65,10); print thif;}'`
NET_IP=`ifconfig ${NET_IF} | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'`

sudo docker kill $(sudo docker ps -q)
sudo docker build -t blebot .
sudo docker run -p 0.0.0.0:80:80 -e LOCALHOST=$NET_IP -e DISCORD_ACCESS_TOKEN=$DISCORD_ACCESS_TOKEN -d -t blebot
