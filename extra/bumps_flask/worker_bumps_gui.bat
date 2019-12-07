docker container rm -f bumps_worker

docker run -it -d --link bumps_db --link redis-server --link rabbit-server --name bumps_worker -e "DATABASE_SERVER=%1" bumps_gui
