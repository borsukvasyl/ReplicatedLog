FROM python:3.6

WORKDIR /opt/workspace/ReplicatedLog
COPY . .
EXPOSE 8000

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py", "secondary"]
