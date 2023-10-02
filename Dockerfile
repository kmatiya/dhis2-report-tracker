FROM python:3.9

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip install -r requirements.txt

CMD [ "python", "./main.py"]
