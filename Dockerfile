FROM python:3.13.10
WORKDIR /bot
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD python3 main.py