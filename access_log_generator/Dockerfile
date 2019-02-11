FROM ubuntu:16.04

# Generator requires building numpy
RUN apt-get update && \
    apt-get install -y \
    python3 python3-numpy pep8 python3-pip python-wheel \
    python-sphinx && \
    pip3 install --upgrade setuptools

# Setup working directory
WORKDIR /usr/src

# Fetch the generator code
RUN apt-get update && apt-get -y install git
RUN git clone https://github.com/kiritbasu/Fake-Apache-Log-Generator.git .
RUN pip3 install --no-cache-dir -r requirements.txt

# Create logs folder to be mounted at /tmp
RUN mkdir logs 
WORKDIR /usr/src/logs

# Run the generator
CMD ["python3", "../apache-fake-log-gen.py", "-n", "0", "-o", "LOG", "-p", "fakelogs"]