FROM mysql

# needed for intialization
ENV MYSQL_ROOT_PASSWORD=root
ENV MYSQL_USER=swispaccer
ENV MYSQL_PASSWORD=swispaccer@123
ENV MYSQL_DATABASE=swispaccer

COPY setup.sql /docker-entrypoint-initdb.d/

# Need to change the datadir to something else that /var/lib/mysql because the parent docker file defines it as a volume.
# https://docs.docker.com/engine/reference/builder/#volume :
#       Changing the volume from within the Dockerfile: If any build steps change the data within the volume after
#       it has been declared, those changes will be discarded.
#RUN ["/usr/local/bin/docker-entrypoint.sh", "mysqld", "--datadir", "/initialized-db", "--aria-log-dir-path", "/initialized-db"]

#FROM mariadb:latest

#COPY --from=builder /initialized-db /var/lib/mysql