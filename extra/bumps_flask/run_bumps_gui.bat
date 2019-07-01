docker container rm -f bumps_gui
docker build --rm -f bumps_gui.dockerfile -t bumps_gui .
docker run -it -d --name bumps_gui -p 8765:8765 -p 4000:4000 -p 4567:4567 bumps_gui
docker exec -i -t bumps_gui bash
rem docker run -d --name bumps_gui -p 8765:8765 -p 4000:4000 -p 4567:4567 bumps_gui
rem docker exec -i -t bumps_redis "redis-cli"
