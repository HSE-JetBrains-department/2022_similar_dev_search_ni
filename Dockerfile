FROM python:3.8
RUN mkdir -p /usr/src/app/

WORKDIR /usr/src/app
COPY . /usr/src/app/

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "repo_processing/main.py"]