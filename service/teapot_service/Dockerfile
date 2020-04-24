FROM ubuntu:18.04
MAINTAINER bay@hackerdom.ru

COPY teapot /home/teapot
RUN chmod +x /home/teapot/tea_httpd
RUN chmod +x /home/teapot/teapot.cgi
RUN chmod -R +r /home/teapot

WORKDIR /home/teapot

CMD /home/teapot/tea_httpd 0.0.0.0:3255

EXPOSE 3255
