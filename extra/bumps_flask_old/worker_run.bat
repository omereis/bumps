echo off
if "%1" == "" (
    echo The variable is empty
	set worker_name="win_bumps_worker"
) ELSE (
	set worker_name=%1
    echo The variable contains %1
)
echo worker name: "%worker_name%"
docker container rm -f  "%worker_name%"
docker build --rm -t bumps_worker -f Dockerfile__worker.bumps .
docker run -d -it --link redis-server --link rabbit-server -h "%worker_name%" --name "%worker_name%" --env BROKER_SERVER=ncnr-r9nano --env BACKEND_SERVER=ncnr-r9nano bumps_worker
rem docker exec -it "%worker_name%" bash
