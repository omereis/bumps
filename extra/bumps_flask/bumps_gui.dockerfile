# Using the latest long-term-support Ubuntu OS
FROM ubuntu:18.04

# Update the apt-get index and then install project dependencies
RUN apt-get update && apt-get install -y man vim git tree

# Create the home directory for the new app user.
RUN mkdir -p /home/bumps_user/bumps_flask

# Set the home directory to our app user's home.
ENV HOME=/home/bumps_user/bumps_flask/bumps_gui

# Set the directory for relative file paths
WORKDIR /home/bumps_user/bumps_flask/bumps_gui

RUN apt-get install -y iputils-ping
# RUN apt install -y python3.7
RUN apt install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt install -y python3.7
RUN ln -s /usr/bin/python3.7 /usr/bin/python
COPY get-pip.py /tmp
RUN apt install -y python3-distutils
RUN python /tmp/get-pip.py

#RUN pip install git+https://github.com/omereis/bumps.git

# Make the 4000 port available from outside the container
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
# RUN pip install celery

# Set the environment variables for Flask
ENV WEBSOCKET_PORT=4567
ENV BUMPS_MP_PORT=4567

# Copy app files to the container
COPY ./ /home/bumps_user/bumps_flask
COPY ./vimrc /etc/vim/vimrc

# Launch the app
# CMD ["python", "app_bumps.py", "-s 0.0.0.0", "-p 4000", "-m 4567"]
