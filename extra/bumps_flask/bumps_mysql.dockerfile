FROM linuxserver/mariadb

#FROM ubuntu:18.04
#RUN apt-get update
#RUN DEBIAN_FRONTEND=noninteractive
RUN apt update
#RUN apt install -y systemd
RUN apt install -y vim man

# Set the home directory to our app user's home.
ENV HOME=/home/bumps_user/

# Set the directory for relative file paths
WORKDIR /home/bumps_user/
# /home/bumps_user/bumps_flask/bumps_gui
COPY ./ $HOME
# COPY ./vimrc /etc/vim/vimrc
# COPY *.sql $HOME
# RUN chmod a+x wait_dock.sh
# RUN mysql -u root -pbumps_root -e "create database bumps_db;"
# RUN sleep 5
RUN mysql --version
# RUN /etc/init.d/mysql start
# RUN mysql -u root -pbumps_root < "create.sql"
# mysql -u root -pbumps_root < "create.sql"
EXPOSE 3306
# ENTRYPOINT mysql -u root -pbumps_root < "create.sql"
