# hash:sha256:8e06940a401ab9fb3e1a4eae8b49d21362ba3df54731e5ed54fb472af6bf68b8
FROM registry.codeocean.allenneuraldynamics.org/codeocean/mambaforge3:22.11.1-4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

RUN conda install -y \
        jupyterlab \
        notebook \
    && conda clean -ya

RUN pip install -U --no-cache-dir \
    jupyter-book

COPY postInstall /
RUN /postInstall
