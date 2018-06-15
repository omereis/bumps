rem docker run --name oe_mariadb -e MYSQL_ROOT_PASSWORD=bumps_pass -d mariadb
docker container rm -f oe_mysql
docker build --rm -t oe_mysql -f Dockerfile_mysql.oe .
docker run -d -it -p 3306 -h oe_mysql --name oe_mysql oe_mysql
docker exec -i -t oe_mysql "bash"
rem docker run -d --link oe_bumps -e MARIADB_ROOT_PASSWORD="masterkey" --name mariadb partlab/ubuntu-mariadb
rem docker run -d -e MARIADB_ROOT_PASSWORD="masterkey" --name oe_mariadb --link oe_bumps oe_mariadb
rem docker run --name some-mariadb -v D:\Omer\Source\omer_bumps\bumps\extra\bumps_flask\mysql\Data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=masterkey -d mariadb