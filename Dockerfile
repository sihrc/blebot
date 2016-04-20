FROM phusion/baseimage

RUN apt-get update -q && \
    apt-get install -y vim git python3-dev python3-setuptools python3-apt build-essential python-dateutil python3-pip supervisor libffi-dev && \
    chmod og+X /root && \
    sudo pip3 install git+https://github.com/Rapptz/discord.py@async && \
    sudo apt-get install -y build-essential libpq-dev

ADD . /blebot
WORKDIR /blebot

RUN pip3 install -r requirements.txt && \
    cp supervisord.conf /etc/supervisord.conf

CMD ["/usr/bin/supervisord"]
