# hash:sha256:de7a61145828532117fcb7c2490145cc6415b5e81f171ed23b5c5e0afb424774
FROM registry.codeocean.allenneuraldynamics.org/codeocean/mambaforge3:22.11.1-4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

RUN pip install -U --no-cache-dir \
    jupyter-book

COPY postInstall /
RUN /postInstall
