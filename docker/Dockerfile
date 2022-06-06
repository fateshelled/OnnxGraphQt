FROM ubuntu:20.04

ARG USERNAME=onnxgraphqt
ARG HOME=/home/${USERNAME}
ARG GID=1000
ARG UID=1000

RUN groupadd -f -g ${GID} ${USERNAME} && \
    useradd -m -s /bin/bash -u ${UID} -g ${GID} -G sudo ${USERNAME} && \
    echo ${USERNAME}:${USERNAME} | chpasswd && \
    echo "${USERNAME}   ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

ENV DEBIAN_FRONTEND noninteractive
RUN apt update && \
    apt install -y \
        # sudo \
        git \
        bash-completion \
        python3-dev \
        python3-pip \
        python3-pyside2* && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

USER ${USERNAME}
WORKDIR ${HOME}
RUN git clone https://github.com/fateshelled/OnnxGraphQt && \
    cd OnnxGraphQt && \
    python3 -m pip install -U pip && \
    python3 -m pip install -U nvidia-pyindex && \
    python3 -m pip install -U Qt.py && \
    python3 -m pip install -U onnx-simplifier && \
    python3 -m pip install -U protobuf==3.20.0 && \
    python3 -m pip install -U -r requirements.txt && \
    rm -rf ~/.cache/pip
