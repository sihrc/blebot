FROM phusion/baseimage
ENV GITHUB_ACCESS_TOKEN "MTcwMDAwNTU5NjgyNzQ4NDE2.CfCU2w.vS9prYUc3hjftnpva_a6_rVWFYs"
RUN apt-get update -q && \
    apt-get install -y vim git python3-dev python3-setuptools python3-apt build-essential python-dateutil python3-pip supervisor libffi-dev && \
    chmod og+X /root && \
    sudo pip3 install git+https://github.com/Rapptz/discord.py@async && \
    sudo apt-get install -y build-essential postgresql postgresql-contrib libpq-dev python-psycopg2 && \
    sudo service postgresql start && \
    sudo -u postgres createuser -s blebot && \
    sudo -u postgres psql -c "ALTER USER blebot WITH PASSWORD 'blerocks';"

ADD . /blebot
WORKDIR /blebot

RUN pip3 install -r requirements.txt && \
    cp supervisord.conf /etc/supervisord.conf

CMD ["/usr/bin/supervisord"]
