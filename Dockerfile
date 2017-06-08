FROM python:3
SHELL ["/bin/bash", "-c"]
RUN useradd -m skybeard
USER skybeard
WORKDIR /home/skybeard
RUN mkdir code db db_binary_entries skybeard_virtualenv
RUN python3 -m venv skybeard_virtualenv_frozen
RUN ls -haltr skybeard_virtualenv_frozen
ADD requirements.txt .
RUN . /home/skybeard/skybeard_virtualenv_frozen/bin/activate && pip install -r requirements.txt