# base image 
FROM python:3.11
MAINTAINER melodia

# setup environment variable  
ENV DockerHOME=/home/app/webapp

# set work directory  
RUN mkdir -p $DockerHOME

# where your code lives  
WORKDIR $DockerHOME  

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  

# install dependencies  
RUN pip install --upgrade pip  

# copy whole project to your docker home directory. 
COPY ../../backend_melodia $DockerHOME
COPY ../../Audios $DockerHOME
COPY ../../frontApi $DockerHOME
COPY ../../Global $DockerHOME
COPY ../../Usuarios $DockerHOME

# run this command to install all dependencies  
RUN pip install -r requirements.txt  

# port where the Django app runs  
EXPOSE 8081  

# start server  
CMD python manage.py runserver  