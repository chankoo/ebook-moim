FROM mysql:latest

ENV MYSQL_DATABASE=ebook_moim \
    MYSQL_ROOT_PASSWORD=root

COPY ./mysql-init-files /docker-entrypoint-initdb.d
COPY ./mysql-confs /etc/mysql/conf.d/

EXPOSE 3306