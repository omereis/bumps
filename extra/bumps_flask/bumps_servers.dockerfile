FROM mysql
##FROM ubuntu:18.04
#
ENV MYSQL_ROOT_PASSWORD=pass
#
ADD bumps_gui/sql/create_all.sql /docker-entrypoint-initdb.d

# docker run --name db_server -e MYSQL_ROOT_PASSWORD=root_pass -d mysql
# docker run -it --rm mysql mysql -hdb_server -uexample-user -p
RUN apt update
RUN apt upgrade
RUN apt update
RUN apt install -y wget
RUN apt install -y build-essential
# Install Redis.
RUN \
  cd /tmp && \
  wget http://download.redis.io/redis-stable.tar.gz && \
  tar xvzf redis-stable.tar.gz && \
  cd redis-stable && \
  make && \
  make install && \
  cp -f src/redis-sentinel /usr/local/bin && \
  mkdir -p /etc/redis && \
  cp -f *.conf /etc/redis && \
  rm -rf /tmp/redis-stable* && \
  sed -i 's/^\(bind .*\)$/# \1/' /etc/redis/redis.conf && \
  sed -i 's/^\(daemonize .*\)$/# \1/' /etc/redis/redis.conf && \
  sed -i 's/^\(dir .*\)$/# \1\ndir \/data/' /etc/redis/redis.conf && \
  sed -i 's/^\(logfile .*\)$/# \1/' /etc/redis/redis.conf

# Define mountable directories.
VOLUME ["/data"]

# Define working directory.
WORKDIR /data

# Define default command.
#CMD ["redis-server", "/etc/redis/redis.conf"]

# Expose ports.
EXPOSE 6379
EXPOSE 3306

