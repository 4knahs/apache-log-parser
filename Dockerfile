FROM python:3
RUN touch /tmp/access.log
WORKDIR /usr/src
ADD . /usr/src
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "main.py", "-f"]
