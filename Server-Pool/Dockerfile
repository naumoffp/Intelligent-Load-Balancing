FROM python:3.10.4-slim-bullseye

# EXPOSE 8080

# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1
# ENV PRODUCTION True
# ENV PORT 8080

WORKDIR /Server-Pool


# RUN apt-get update
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ENTRYPOINT [ "python", "./minister.py"]
CMD ["python3", "main.py"]
