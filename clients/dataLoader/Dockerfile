FROM centos:7
RUN yum update -y
RUN yum install -y python3
RUN yum install git wget make gcc bzip2 zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel readline-devel sqlite sqlite-devel libffi-devel gcc-c++ python-devel python-pip -y
WORKDIR /root
RUN wget https://www.python.org/ftp/python/3.9.5/Python-3.9.5.tgz
RUN tar -xvf Python-3.9.5.tgz
WORKDIR Python-3.9.5
RUN ./configure --enable-optimizations
RUN make altinstall
RUN alternatives --install /usr/local/bin/python3 python3 /usr/local/bin/python3.9 1
RUN alternatives --install /usr/local/bin/pip3 pip3 /usr/local/bin/pip3.9 1
WORKDIR /root
# clone the repo
RUN mkdir gauntlet
ADD gauntlet /root/gauntlet/
WORKDIR gauntlet
# RUN chmod -R 777 *

# To support CB py-sdk package
RUN yum install -y gcc gcc-c++ python3-devel python3-pip cmake

# To support py-ldap package
RUN yum install -y python-devel openldap-devel

# install dependencies in the virtual env
ENV TMPDIR /root/tmp
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools wheel
RUN pip3 install -r services/profile/requirements.txt

ENV PYTHONPATH /root/gauntlet
CMD ["python3", "./clients/dataLoader/data_loader.py"]
