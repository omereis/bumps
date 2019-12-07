# celery -A bumps_celery worker -l info -E 
# python app_bumps.py --server 0.0.0.0 --port 4000 --mp_port 4567
if ! [ -z ${RUN_WS} ]; then
#	echo "running as server";
	celery -A bumps_celery worker -l info -E &
	celery flower -A bumps_celery worker -l info -E --port=4100 &
	python app_bumps.py --server 0.0.0.0 --port 4000 --mp_port 4567
else
	celery -A bumps_celery worker -l info -E 
#	echo "RUN_WS is unset";
fi

