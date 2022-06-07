FROM python:3.10.4-slim-bullseye

# EXPOSE 8080

# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1
# ENV PRODUCTION True
# ENV PORT 8080

WORKDIR /Request-Spawner


# RUN apt-get update
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "request-spawner.py"]
