FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV SMTP_HOSTNAME=0.0.0.0
ENV SMTP_PORT=2525
ENV PYTHONUNBUFFERED=1

EXPOSE 2525

HEALTHCHECK --interval=2m --timeout=5s \
  CMD python3 /app/healthcheck.py || exit 1

CMD [ "python3", "/app/main.py" ]
