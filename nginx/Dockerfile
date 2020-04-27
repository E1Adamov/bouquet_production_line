FROM nginx:stable

COPY ./config /etc/nginx
RUN cd /etc/nginx/conf.d/sites-enabled && ln -s ../sites-available/reverseproxy.conf
