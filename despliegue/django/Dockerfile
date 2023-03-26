# base image 
FROM python:3.11
MAINTAINER melodia

# setup environment variable  
ENV DOCKERHOME=/usr/local/melodia/backend/

# set work directory  
RUN mkdir -p $DOCKERHOME

# where your code lives  
WORKDIR $DOCKERHOME  

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  

# install dependencies  
RUN pip install --upgrade pip  

# copy whole project to your docker home directory. 
COPY requirements.txt $DOCKERHOME
COPY manage.py $DOCKERHOME
COPY backend_melodia/ $DOCKERHOME
COPY DAOS/ $DOCKERHOME
COPY frontApi/ $DOCKERHOME
COPY Configuracion/ $DOCKERHOME
COPY Usuarios/ $DOCKERHOME

# run this command to install all dependencies  
RUN pip install -r requirements.txt

# port where the Django app runs  
EXPOSE 8081

# start server
CMD python manage.py runserver 8081