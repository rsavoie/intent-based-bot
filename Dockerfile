FROM python:3

WORKDIR /usr/src/app

COPY . .

ENV FLASK_APP intentbasedbot
ENV FLASK_DEBUG True

RUN pip install -e .

EXPOSE 5000

CMD [ "flask", "run", "--host=0.0.0.0" ]