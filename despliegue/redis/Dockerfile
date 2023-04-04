FROM redis:alpine
MAINTAINER melodia
COPY redis.conf /usr/local/etc/redis/redis.conf
COPY users.acl /usr/local/etc/redis/users.acl
COPY appendonlydir /data/appendonlydir
CMD [ "redis-server", "/usr/local/etc/redis/redis.conf" ]
