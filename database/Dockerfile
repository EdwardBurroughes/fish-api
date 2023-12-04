FROM postgis/postgis:16-3.4-alpine
COPY ./database/sql/ /docker-entrypoint-initdb.d
ENV POSTGRES_PASSWORD=mysecret