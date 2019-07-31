#python app_bumps.py --server 0.0.0.0 --port 4000 --mp_port 4567
celery -A bumps_celery worker -l info


