FROM python:3.7-slim
LABEL maintainer="ENOFLAG <mail@enoflag.de>"

# copy our files in.
WORKDIR /checker
COPY ./requirements.txt /checker/requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

ENTRYPOINT [ "python", "checker.py" ]