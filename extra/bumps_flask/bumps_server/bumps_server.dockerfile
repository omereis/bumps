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
RUN pip install --upgrade pip

WORKDIR /home/oe/
ENV HOME=/home/oe/
COPY ./ /home/oe

RUN python /home/oe/get-pip.py
RUN pip install websockets
RUN pip install sqlalchemy
RUN pip install pymysql
RUN pip install mysql-connector-python
RUN pip install bumps numpy scipy matplotlib nest_asyncio

# Make the 8765 port available from outside the container
EXPOSE 5678
EXPOSE 5000

#from sqlalchemy import create_engine
#engine = create_engine('mysql+pymysql://bumps:bumps_dba@NCNR-R9nano.campus.nist.gov:3306/bumps_db')
# /home/oe/unix/examples/curvefit/curve.py
# ['/usr/local/bin/bumps', '/home/oe/examples/test/curve.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/oe/examples/test/results', '--fit=dream']