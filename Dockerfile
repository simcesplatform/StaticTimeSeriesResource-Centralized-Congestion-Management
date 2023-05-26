FROM python:3.7.6

RUN mkdir -p /resource_centralized
RUN mkdir -p /init
RUN mkdir -p /logs
RUN mkdir -p /domain-messages

# install the python libraries
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

COPY resource_centralized/ /resource_centralized/
COPY init/ /init/
COPY domain-messages/ /domain-messages/

WORKDIR /

CMD [ "python3", "-u", "-m", "resource_centralized.component" ]
