# cnn_gpu
## Convolution Neural Network models workspace on nvidia_docker

Python based convolution neural networks configured to run with a custom nvidia-docker instance. 
The Dockerfile under docker was built to run on a System76 Oryx Pro with an Nvidia 1060 gpu and an Intel i7 processor.  It's been design to run deeplearning experiments from Adrian Rosbrook's deep learning series. Similar setups should probably run it OK, but you may need to make changes to the Dockerfile under keras_src/docker if you experience issues.

To build : 
```cd docker && nvidia-docker build -t cnn_gpu:latest . ```

There is a start up script (./start_keras_docker.sh) but note that it has -v setup to map local directories to the container's /root/src and /root/data folders.  You'll  need to make sure the host paths exist or change them appropriately to use the examples.

## Checking the GPU
```python3 tensor_flow_device.py ```` will verify tensorflow is installed and correctly show if it's using the gpu.
