FROM python:3.10.10-bullseye

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install -r requirements.txt

COPY . /app
EXPOSE 8080:8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "-w", "4", "wsgi:app"]



