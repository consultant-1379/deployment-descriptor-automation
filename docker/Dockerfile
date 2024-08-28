FROM ubuntu:latest

RUN apt-get update
RUN apt-get dist-upgrade -y
RUN apt-get install -y python3 python3-venv python3-pip \
&& \
    apt-get install -y git \
&& \
    apt-get install -y maven \
&& \
    apt-get install -y p7zip-full p7zip-rar \
&& \
    apt-get install -y wget \
&& \
    apt-get install -y rpm2cpio \
&& \
    apt-get install -y cpio

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install wget requests

RUN apt-get clean && \
        rm -rf /var/lib/apt/lists/*

COPY python/main.py /
COPY deploymentDescriptions /deploymentDescriptions
COPY deployment-support-tooling /deployment-support-tooling
COPY defaultConfigurableEntities /defaultConfigurableEntities

ENTRYPOINT [ "python3", "main.py" ]
