docker rm -f bumps_alpha
docker build --rm -f bumps_alpha_client.dockerfile -t bumps_alpha .
rem docker run -it -d --name bumps_alpha bumps_alpha
docker run -it -d --link bumps_gui --name bumps_alpha bumps_alpha
rem docker run -it -d --name docker_refsrv
docker exec -it bumps_alpha bash