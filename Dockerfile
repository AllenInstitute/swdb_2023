FROM ghcr.io/walkerlab/docker-pytorch-jupyter-cuda:cuda-11.8.0-pytorch-1.13.0-torchvision-0.14.0-torchaudio-0.13.0-ubuntu-20.04
COPY . /src/swdb_2023

# shared
RUN pip install --upgrade pip
# specific
RUN pip install cython allensdk

RUN pip install -e /src/swdb_2023