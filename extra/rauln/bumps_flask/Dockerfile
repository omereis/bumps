FROM ubuntu:16.04

RUN apt-get update && apt-get install -y python-pip python-dev libssl-dev

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY setup.py /usr/src/app
COPY app /usr/src/app

EXPOSE 5000

WORKDIR /usr/src/app

ENV FLASK_APP=server.py
ENV FLASK_DEBUG=1

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
