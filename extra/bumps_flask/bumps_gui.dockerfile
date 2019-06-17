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
ENV HOME=/home/app_user

# Set the directory for relative file paths
#WORKDIR /home/app_user/bumps_flask/bumps_flask
WORKDIR /home/app_user/bumps_flask

# Create the folder for the html templates and static assets
RUN mkdir templates/ && mkdir static/

# Install the app dependencies using pip
RUN pip install -U pip
RUN pip install --upgrade pip
#COPY requirements.txt /home/app_user/bumps_flask/
###############
#RUN pip install --no-cache-dir -r ../requirements.txt
###############
RUN pip install flask-socketio
RUN pip install git+https://github.com/omereis/bumps.git

RUN cd /tmp && touch inbar.txt
RUN apt install -y wget
# miniconda installation
# source: https://docs.anaconda.com/anaconda/install/silent-mode/
RUN mkdir /tmp/miniconda && cd /tmp/miniconda && wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
RUN bash ~/miniconda.sh -b -p $HOME/miniconda
ENV PATH="$PATH:/home/app_user/miniconda/bin/"
# conda install python=3.7 anaconda=custom -y
# RUN conda init bash
#RUN conda init bash && conda install python=3.7 anaconda=custom -y && conda create -n bumps_server numpy scipy pandas scikit-learn notebook -y

RUN apt install -y python3.7
RUN rm /usr/bin/python
RUN ln -s /usr/bin/python3.7 /usr/bin/python
COPY get-pip.py /tmp
RUN apt install -y python3-distutils
RUN python /tmp/get-pip.py

#RUN conda install python=3.7 anaconda=custom -y
#RUN conda update conda -y
#RUN conda env list
#RUN conda create -y -n bumps_server pip && /bin/bash -c "source activate bumps_server" && python --version
#RUN conda env list && python --version

#RUN bash && /bin/bash -c "conda activate bumps_server" && pip install websockets sqlalchemy pymysql mysql-connector-python bumps numpy scipy matplotlib nest_asyncio

#RUN pip install websockets
#RUN pip install sqlalchemy
#RUN pip install pymysql
#RUN pip install mysql-connector-python
#RUN pip install bumps numpy scipy matplotlib nest_asyncio

# Copy app files to the container
COPY ./ /home/app_user/bumps_flask
COPY ./vimrc /etc/vim/vimrc

#RUN chmod a+x flask_run
# Make the 4000 port available from outside the container
EXPOSE 4000

# Create a new user called 'app_user' and set it up on the OS
# RUN groupadd -r app_user && useradd --no-log-init -r -g app_user app_user

# Install the application locally
RUN touch rachel.inbar
#RUN pip install --no-cache-dir -r ../requirements.txt
RUN touch req.txt
RUN pip install -r requirements.txt
##############################################################
##############################################################

RUN pip install websockets
RUN pip install sqlalchemy
RUN pip install pymysql
RUN pip install mysql-connector-python
RUN pip install bumps numpy scipy matplotlib nest_asyncio

# Log in with 'app_user' for the rest of the process
# USER app_user

# Set the environment variables for Flask
ENV FLASK_APP=bumps_flask
ENV FIT_RESULTS_DIR=/home/app_user/bumps_flask/bumps_flask/static/fit_results


# Launch the app
# CMD ["mod_wsgi-express", "start-server", "--host", "0.0.0.0", "--port", "5000", "bumps_flask.wsgi"]
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "bumps_flask:app"]

