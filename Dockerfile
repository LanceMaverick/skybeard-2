FROM python:3

# Use bash as the shell because we will need to source a virtualenv later
SHELL ["/bin/bash", "-c"]

# Create a skybeard user
RUN useradd -m skybeard
USER skybeard
WORKDIR /home/skybeard

# Make a few directories which will be mounted to later
RUN mkdir code db db_binary_entries skybeard_virtualenv

# Create a base virtualenv. Normally, there's no need for a virtualenv in a
# docker container, but since any beards that run can add to the requirements,
# we'll need a virutalenv tied to a persistant container
RUN python3 -m venv skybeard_virtualenv_frozen
ADD requirements.txt .
RUN . /home/skybeard/skybeard_virtualenv_frozen/bin/activate && pip install -r requirements.txt
