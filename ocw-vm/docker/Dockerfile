# Dockerfile for installing a Docker instance of OCW
#
# BY: Rishi Verma, riverma@apache.org
# CREATED: Sept 3rd, 2015
# DESCRIPTION:   
#  This file serves as a configuration point for 
#  installing OCW as a Docker container. The Docker 
#  container (http://docker.io) version of OCW supports 
#  all command-line Unix-executable tools part of OCW
# REQUIREMENTS: 
#  * Docker 1.8+
#  * A Linux operating-system, with kernel version: 3.10+
#    - TIP: check your Kernel version via `uname -a` 

FROM ubuntu:12.04
RUN apt-get update && apt-get install -y make \
libblas-dev \
liblapack-dev \
gfortran \
g++ \
build-essential \
python-dev \
git \
vim \
ia32-libs \
sudo \
wget \
expect
#RUN git clone http://git-wip-us.apache.org/repos/asf/climate.git /root/climate
RUN git clone https://github.com/riverma/climate.git /root/climate

RUN cd /root/climate/easy-ocw && ./install-ubuntu.sh -q
