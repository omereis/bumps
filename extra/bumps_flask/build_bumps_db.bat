docker container rm -f bumps_db
docker build --rm -f bumps_db.dockerfile -t bumps_db .
docker run -it -d -h bumps_db_host --name bumps_db --env MYSQL_ROOT_PASSWORD=bumps_root -p 5306:3306 bumps_db
docker exec -i -t bumps_db bash
