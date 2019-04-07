FROM ubuntu:18.04
MAINTAINER bay@hackerdom.ru

RUN useradd teapot

ADD teapot /home/teapot
RUN chown -R teapot:teapot /home/teapot/pots
RUN chmod +x /home/teapot/tea_httpd
RUN chmod +x /home/teapot/teapot.cgi
RUN chmod -R +r /home/teapot

WORKDIR /home/teapot
USER teapot

CMD /home/teapot/tea_httpd 0.0.0.0:3255

EXPOSE 3255