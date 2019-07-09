# Using the latest long-term-support Ubuntu OS
FROM ubuntu:18.04

RUN apt -y update
RUN apt -y upgrade
RUN apt install -y vim
RUN apt install -y tree curl
RUN apt install -y python3.7
RUN ln -s /usr/bin/python3.7 /usr/bin/python
RUN apt install -y mysql-client

RUN apt install -y python3-pip
RUN ln -s /usr/bin/pip3 /usr/bin/pip

COPY get-pip.py /tmp
RUN apt install -y python3-distutils
RUN apt install -y sqlite3
RUN python /tmp/get-pip.py

RUN pip install -U pip
RUN pip install --upgrade pip

RUN pip install websockets
RUN pip install random_word
RUN pip install readchar
RUN pip install tabulate
RUN pip install websocket websocket-client

WORKDIR /home/bumps_alpha
ENV HOME=/home/bumps_alpha/
COPY ./ /home/bumps_alpha
COPY ./vimrc /etc/vim/vimrc
# python send_fit_job.py --command server --tag alpha --server bumps_gui --port 4567 -y

