rem docker exec -i -t bumps_redis "redis-cli"
rem bumps cf1.py --batch --stepmon --burn=100 --steps=100 --store=./cf1_results --fit=newton
rem apt-get install python-numpy python-scipy python-matplotlib
rem bumps cf1.py --batch --stepmon --burn=100 --steps=100 --store=cf1_results --fit=newton
rem docker run --link redis-server --link rabbit-server -e "BACKEND_SERVER=redis-server" -p 5000:5000 --name oe_bumps oe_bumps
rem app = Celery('proj', broker='amqp://rabbit-server', backend='redis://redis-server')


rem docker run -d -it -h oe_bumps --name oe_bumps oe_bumps


rem GRANT ALL PRIVILEGES ON *.* TO 'u'@'localhost' WITH GRANT OPTION;
rem grant all privileges on *.* to 'u'@'localhost' with grant options;
rem 172.22.144.1
rem conn = mysql.connector.connect(host=172.22.144.1, database='bumps_db', user='bumps',password='bumps_dba')