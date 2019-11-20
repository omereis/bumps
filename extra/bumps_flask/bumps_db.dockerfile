FROM mysql
#
ENV MYSQL_ROOT_PASSWORD=pass
#
ADD bumps_gui/sql/create_all.sql /docker-entrypoint-initdb.d

EXPOSE 3306

# docker run --name db_server -e MYSQL_ROOT_PASSWORD=root_pass -d mysql
# docker run -it --rm mysql mysql -hdb_server -uexample-user -p
