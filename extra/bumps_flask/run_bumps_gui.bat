docker container rm -f bumps_gui
docker build --rm -f bumps_gui.dockerfile -t bumps_gui .

docker run -it -d -h bumps_host --link bumps_db --link redis-server --link rabbit-server --name bumps_gui -p 5672 -p 4000:4000 -p 4100:4100 -e "RUN_WS=1" -e "DATABASE_SERVER=%1" -p 4567:4567 bumps_gui

rem docker exec -i -t bumps_gui bash
