FROM python:latest

RUN apt-get update && apt-get install -y stress cpulimit psmisc

WORKDIR stress
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD src/ .
EXPOSE 5000
CMD ["/usr/local/bin/python", "server.py"]
