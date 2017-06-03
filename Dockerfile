 FROM python:3
 ENV PYTHONUNBUFFERED 1
 RUN mkdir /code
 RUN chown -R root:root code
 ADD requirements.txt /
 RUN pip install -r requirements.txt
 ADD run_on_docker.sh /