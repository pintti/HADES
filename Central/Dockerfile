FROM python:3.10.10-bullseye

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install -r requirements.txt

COPY . /app
EXPOSE 8000:8000
CMD ["gunicorn", "--preload", "--bind", "0.0.0.0:8000", "-w", "1", "wsgi:app"]



