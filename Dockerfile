FROM python:3

# set a directory for the app
WORKDIR /srv

#RUN mkdir /srv

COPY . /srv/


# install dependencies
RUN pip install Flask
RUN pip install requests
#RUN pip install Flask_SQLAlchemy
#RUN pip install psycopg2
#RUN pip install -U flask-cors
#RUN pip install Flask-Sockets

# tell the port number the container should expose
#EXPOSE 5000

# run the command
CMD ["python3", "server.py"]