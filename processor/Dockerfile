FROM python:3.9.16-bullseye

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install -r requirements.txt

COPY . /app
EXPOSE 8080:8080
CMD ["gunicorn", "--preload", "--bind", "0.0.0.0:8080", "-w", "1", "wsgi:app", "--log-level", "info", "--capture-output"]



