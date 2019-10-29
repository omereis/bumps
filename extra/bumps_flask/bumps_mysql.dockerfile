FROM linuxserver/mariadb

#FROM ubuntu:18.04
#RUN apt-get update
#RUN DEBIAN_FRONTEND=noninteractive
RUN apt update
#RUN apt install -y systemd
RUN apt install -y vim man
# RUN apt install -y tree curl
EXPOSE 3306
