# pull official base image
FROM python:stretch

# set work directory
COPY . /app
WORKDIR /app


# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#  Entry Point
CMD ["gunicorn", "-b", ":8080", "main:APP"]
