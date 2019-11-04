docker container rm -f bumps_gui
docker build --rm -f bumps_gui.dockerfile -t bumps_gui .
rem docker run -it -d -h bumps_host --name bumps_gui -p 5672 -p 4000:4000 -p 4567:4567 bumps_gui
docker run -it -d -h bumps_host --link bumps_mysql --link redis-server --link rabbit-server --name bumps_gui -p 5672 -p 4000:4000 -p 4567:4567 bumps_gui
rem docker run -it -d -h bumps_host --name bumps_gui --link redis-server -p 5672 --link rabbit-server -p 4000:4000 -p 4567:4567 bumps_gui
docker exec -i -t bumps_gui bash
