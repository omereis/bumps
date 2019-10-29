rem docker run -d --name maria_db --env MYSQL_ROOT_PASSWORD=root linuxserver/mariadb
docker container rm -f bumps_mysql
docker build --rm -f bumps_mysql.dockerfile -t bumps_mysql .
docker run -it -d -h bumps_mysql_host --name bumps_mysql --env MYSQL_ROOT_PASSWORD=root bumps_mysql
docker exec -i -t bumps_mysql bash
