FROM tiangolo/uvicorn-gunicorn-fastapi:python3.6

COPY requirements.txt .
COPY README.md .

RUN pip3 install -U pip \
    && pip3 install -r requirements.txt

COPY . /app/
