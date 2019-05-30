# Using the latest long-term-support Ubuntu OS
FROM ubuntu:18.04

RUN apt -y update
RUN apt -y upgrade
# RUN apt install -y software-properties-common
# RUN add-apt-repository -y ppa:deadsnakes/ppa
#RUN apt install -y vim man
RUN apt install -y vim
RUN apt install -y tree curl
RUN apt install -y python3.6
RUN ln -s /usr/bin/python3.6 /usr/bin/python
#RUN curl -sS https://bootstrap.pypa.io/get-pip.py >>setup.py
#RUN python setup.py

RUN apt install -y python3-pip
RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN pip install --upgrade pip
RUN pip install websockets
RUN pip install sqlalchemy
RUN pip install pymysql
RUN pip install mysql-connector-python

WORKDIR /home/oe/
ENV HOME=/home/oe/
COPY ./ /home/oe

# Make the 8765 port available from outside the container
EXPOSE 5678
EXPOSE 5000

#from sqlalchemy import create_engine
#engine = create_engine('mysql+pymysql://bumps:bumps_dba@NCNR-R9nano.campus.nist.gov:3306/bumps_db')