# Using the latest long-term-support Ubuntu OS
FROM ubuntu:18.04

# Update the apt-get index and then install project dependencies
RUN apt-get update && apt-get install -y man vim git tree
RUN apt install -y mysql-client

# Create the home directory for the new app user.
RUN mkdir -p /home/bumps_user/bumps_flask

# Set the home directory to our app user's home.
ENV HOME=/home/bumps_user/bumps_flask/bumps_gui

# Set the directory for relative file paths
WORKDIR /home/bumps_user/bumps_flask/bumps_gui

RUN apt-get install -y iputils-ping

RUN apt install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt install -y python3.7
RUN ln -s /usr/bin/python3.7 /usr/bin/python

RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime
RUN apt-get install -y tzdata
RUN dpkg-reconfigure --frontend noninteractive tzdata
RUN apt install -y python3-distutils
COPY get-pip.py /tmp
RUN python /tmp/get-pip.py
RUN rm -rf /tmp/*

EXPOSE 4000

RUN pip install websockets sqlalchemy pymysql
RUN pip install mysql-connector-python
RUN pip install bumps numpy scipy matplotlib nest_asyncio
RUN pip install flask flask_redis flask_jwt_extended flask_restful flask_wtf
RUN pip install celery readchar
RUN pip install websocket websocket-client

#required for psutil
RUN apt install -y python3.7-dev build-essential
RUN pip install psutil

RUN pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-18.04 wxPython
RUN pip install refl1d
RUN pip install cryptography
RUN pip install flower

# Copy app files to the container
COPY ./ /home/bumps_user/bumps_flask
# COPY ./vimrc /etc/vim/vimrc

# Launch the app
ENTRYPOINT ["/bin/sh","/home/bumps_user/bumps_flask/bumps_gui/run_all.sh"]

