FROM python:3.8-slim-buster

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY main.py main.py
COPY src src

ENTRYPOINT ["python"]
CMD ["main.py"]

