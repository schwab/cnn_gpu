#cd ./keras_src/docker && make SRC=/mnt/extradrive1/projects/pyimagesearch DATA=/mnt/extradrive1/projects/pyimagesearch/data bash
cd ./docker && nvidia-docker run -it -p 8888:8888 -p 6006:6006 -v /mnt/extradrive1/projects/pyimagesearch/:/root/src/ -v /mnt/extradrive1/projects/pyimagesearch/data/:/root/data/  cnn_gpu:latest bash
