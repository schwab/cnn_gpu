# FROM defines the base image
FROM gcr.io/tensorflow/tensorflow:latest-gpu
MAINTAINER Jihong Ju <daniel.jihong.ju@gmail.com>

# Disable interactive interface
ARG DEBIAN_FRONTEND=noninteractive

# RUN executes a shell command
# You can chain multiple commands together with &&
# A \ is used to split long lines to help with readability
RUN apt-get update && apt-get install -y \
    # tools
    git \
    vim \
    python-setuptools \
    python-virtualenv \
    graphviz \
    tmux  build-essential cmake git unzip pkg-config \
    libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    libxvidcore-dev libx264-dev \
    libgtk-3-dev \
    libhdf5-serial-dev graphviz \
    libopenblas-dev libatlas-base-dev gfortran \
    python-tk python3-tk python-imaging-tk 
RUN apt-get install -y qt5-default
# Install keras and theano dependencies not included in
# https://github.com/tensorflow/tensorflow/blob/master/tensorflow/tools/docker/Dockerfile.gpu
RUN pip install -U pip && pip --no-cache-dir install --upgrade \
    pandas \
    h5py \
    pyyaml \
    virtualenv \
    graphviz \
    pydot \
    keras-tqdm

# Enable the widgetsnbextension for notebook
RUN jupyter nbextension enable --py --sys-prefix widgetsnbextension

# Install theano and keras
RUN pip --no-cache-dir install --no-deps \
    theano \
    keras \
    git+https://www.github.com/farizrahman4u/keras-contrib.git

# Set keras backend to tensorflow by default
ENV KERAS_BACKEND tensorflow
# Install OpenCV
RUN git clone --depth 1 https://github.com/opencv/opencv.git /root/opencv && \
       cd /root/opencv && \
       mkdir build && \
       cd build && \
       cmake -D CMAKE_BUILD_TYPE=RELEASE -D WITH_QT=ON -D WITH_OPENGL=ON -D FORCE_VTK=ON -D WITH_TBB=ON -D WITH_GDAL=ON -D WITH_XINE=ON -D BUILD_EXAMPLES=ON -D CMAKE_LIBRARY_PATH=/usr/local/cuda/lib64/stubs -D OPENCV_TRAITS_ENABLE_DEPRECATED=OFF .. && \
       make -j"$(nproc)"  && \
       make install && \
       ldconfig && \
       echo 'ln /dev/null /dev/raw1394' >> ~/.bashrc
RUN pip install --no-cache-dir imutils


# Add /root/workspace to PYTHONPATH for convenience
ENV PYTHONPATH /root/workspace:$PYTHONPATH

# Set the working directory
WORKDIR /root/workspace

# CMD defines the default command to be run in the container
# CMD is overridden by supplying a command + arguments to
# `docker run`, e.g. `nvcc --version` or `bash`
CMD ["/run_jupyter.sh"]
