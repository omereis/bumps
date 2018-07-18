docker container rm -f bumps_gui
docker build --rm -t bumps_gui -f Dockerfile.bumps .
docker run -d -it -p 5000:5000 -h bumps_gui --name bumps_gui bumps_gui
docker exec -i -t bumps_gui bash

