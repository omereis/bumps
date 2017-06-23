# Using the latest long-term-support Ubuntu OS
FROM ubuntu:16.04

# Update the apt-get index and then install project dependencies
RUN apt-get update && apt-get install -y \
    apache2 \
    apache2-dev \
    libssl-dev \
    python-dev \
    python-pip

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
COPY requirements.txt /home/app_user/bumps_flask/
RUN pip install --no-cache-dir -r ../requirements.txt

# Include mod_wsgi to run Flask behind Apache in this container
# RUN pip install mod_wsgi

# Copy app files to the container
COPY setup.py /home/app_user/bumps_flask
COPY config.py /home/app_user/bumps_flask
COPY bumps_flask/static static
COPY bumps_flask/templates templates
COPY bumps_flask/*.py ./
# COPY bumps_flask/app_wsgi.wsgi ./

# Make the 5000 port available from outside the container
EXPOSE 5000

# Create a new user called 'app_user' and set it up on the OS
RUN groupadd -r app_user && useradd --no-log-init -r -g app_user app_user

# Install the application locally
RUN pip install --no-cache-dir -e ..

# Log in with 'app_user' for the rest of the process
USER app_user

# Set the environment variables for Flask
ENV FLASK_APP=bumps_flask
# DEV
ENV FLASK_DEBUG=1
# DEV
ENV BUMPS_FLASK_DEV=1

# Launch the app
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
