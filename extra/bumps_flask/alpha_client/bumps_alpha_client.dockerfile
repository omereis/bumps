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
RUN python /tmp/get-pip.py

RUN pip install -U pip
RUN pip install --upgrade pip

RUN pip install websockets
RUN pip install random_word
RUN pip install readchar

WORKDIR /home/oe/
ENV HOME=/home/oe/
COPY ./ /home/oe
COPY ./vimrc /etc/vim/vimrc

# Make the 5678 port available from outside the container
#EXPOSE 5678
# EXPOSE 5555
#apt -y install software-properties-common dirmngr apt-transport-https lsb-release ca-certificates