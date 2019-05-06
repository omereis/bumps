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
RUN mkdir -p /home/app_user

# Set the home directory to our app user's home.
ENV HOME=/home/app_user

# Set the directory for relative file paths
WORKDIR /home/app_user/bumps_flask/bumps_flask

# Create the folder for the html templates and static assets
RUN mkdir templates/ && mkdir static/

# Install the app dependencies using pip
RUN pip install -U pip
RUN pip install --upgrade pip
COPY requirements.txt /home/app_user/bumps_flask/
RUN pip install --no-cache-dir -r ../requirements.txt
RUN pip install flask-socketio
RUN pip install git+https://github.com/omereis/bumps.git

# Include mod_wsgi to run Flask behind Apache in this container
# RUN pip install mod_wsgi

# Copy app files to the container
COPY ./ /home/app_user/bumps_flask
COPY ./vimrc /etc/vim/vimrc

#RUN chmod a+x flask_run
# Make the 4000 port available from outside the container
EXPOSE 4000

# Create a new user called 'app_user' and set it up on the OS
RUN groupadd -r app_user && useradd --no-log-init -r -g app_user app_user

# Install the application locally
RUN pip install --no-cache-dir -e ..

# Log in with 'app_user' for the rest of the process
# USER app_user

# Set the environment variables for Flask
ENV FLASK_APP=bumps_flask


# Launch the app
# CMD ["mod_wsgi-express", "start-server", "--host", "0.0.0.0", "--port", "5000", "bumps_flask.wsgi"]
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "bumps_flask:app"]
