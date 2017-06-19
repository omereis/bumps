FROM python:2.7

WORKDIR ~/.bumps_web

ADD . ~/.bumps_web

RUN pip install -r requirements.txt

EXPOSE 80
ENV FLASK_APP bumps_flask/server.py

CMD ["flask run", "bumps_flask/server.py"]
