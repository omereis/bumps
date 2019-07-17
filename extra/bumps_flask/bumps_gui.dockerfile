# Using the latest long-term-support Ubuntu OS
FROM ubuntu:18.04

# Update the apt-get index and then install project dependencies
RUN apt-get update && apt-get install -y \
    apache2 \
    apache2-dev \
    libssl-dev \
    git        \
    python-dev \
    python-pip \
    vim
RUN apt install -y tree

#RUN apt-get install vim
# Create the home directory for the new app user.
RUN mkdir -p /home/app_user/bumps_flask

# Set the home directory to our app user's home.
ENV HOME=/home/app_user/bumps_flask/bumps_gui

# Set the directory for relative file paths
WORKDIR /home/app_user/bumps_flask/bumps_gui

# Install the app dependencies using pip
RUN pip install -U pip
RUN pip install --upgrade pip
RUN pip install flask-socketio
RUN pip install git+https://github.com/omereis/bumps.git

RUN apt install -y python3.7
RUN rm /usr/bin/python
RUN ln -s /usr/bin/python3.7 /usr/bin/python
COPY get-pip.py /tmp
RUN apt install -y python3-distutils
RUN python /tmp/get-pip.py

# Copy app files to the container
COPY ./ /home/app_user/bumps_flask
COPY ./vimrc /etc/vim/vimrc

#RUN chmod a+x flask_run
# Make the 4000 port available from outside the container
EXPOSE 4000

# Create a new user called 'app_user' and set it up on the OS
# RUN groupadd -r app_user && useradd --no-log-init -r -g app_user app_user

#RUN pip install -r requirements.txt

RUN pip install websockets sqlalchemy pymysql
RUN pip install mysql-connector-python
RUN pip install bumps numpy scipy matplotlib nest_asyncio
RUN pip install flask flask_redis flask_jwt_extended flask_restful flask_wtf
RUN pip install celery readchar
RUN pip install websocket websocket-client

# Log in with 'app_user' for the rest of the process
# USER app_user

# Set the environment variables for Flask
ENV WEBSOCKET_PORT=4567
#ENV FLASK_ENV=development
ENV BUMPS_MP_PORT=4567

# Launch the app
# CMD ["mod_wsgi-express", "start-server", "--host", "0.0.0.0", "--port", "5000", "bumps_flask.wsgi"]
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "bumps_flask:app"]


