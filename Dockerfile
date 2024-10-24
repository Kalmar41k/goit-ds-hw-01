FROM python:3.11.9

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY . .

EXPOSE 5000

ENTRYPOINT ["python", "main.py"]
