docker rm -f bumps_alpha
docker run -it -d --link bumps_gui --name bumps_alpha bumps_alpha
docker exec -it bumps_alpha bash