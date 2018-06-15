rem docker run --name oe_mariadb -e MYSQL_ROOT_PASSWORD=bumps_pass -d mariadb
docker container rm -f oe_mysql
docker build --rm -t oe_mysql -f Dockerfile_mysql.oe .
docker run -d -it -p 3306 -h oe_mysql --name oe_mysql oe_mysql
docker exec -i -t oe_mysql "bash"
rem docker run -d --link oe_bumps -e MARIADB_ROOT_PASSWORD="masterkey" --name mariadb partlab/ubuntu-mariadb
rem docker run -d -e MARIADB_ROOT_PASSWORD="masterkey" --name oe_mariadb --link oe_bumps oe_mariadb
rem docker run --name mariadb -v /home/one4/omer_bumps/extra/bumps_flask/mysql/data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=masterkey -d mariadb
rem cnx = mysql.connector.connect(user='bumps', password='bumps_dba', host='127.0.0.1', database='bumps_db')