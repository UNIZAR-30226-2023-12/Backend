# base image 
FROM python:3.10-slim
MAINTAINER melodia

# setup environment variable  
ENV DOCKERHOME=/usr/local/melodia/backend

# set work directory  
RUN mkdir -p $DOCKERHOME

# where your code lives  
WORKDIR $DOCKERHOME  

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  

# install dependencies  
RUN pip3 install --upgrade pip  

# copy whole project to your docker home directory. 
COPY ./requirements.txt $DOCKERHOME
COPY ./manage.py $DOCKERHOME
COPY ./Audios/ $DOCKERHOME/Audios/
COPY ./backend_melodia/ $DOCKERHOME/backend_melodia/
COPY ./Configuracion/ $DOCKERHOME/Configuracion/
COPY ./DAOS/ $DOCKERHOME/DAOS/
COPY ./frontApi/ $DOCKERHOME/frontApi/
COPY ./Global/ $DOCKERHOME/Global/
COPY ./recomendador/ $DOCKERHOME/recomendador/
COPY ./Usuarios/ $DOCKERHOME/Usuarios/

# run this command to install all dependencies  
RUN pip3 install -r requirements.txt

# port where the Django app runs  
EXPOSE 8081

# start server
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8081"]