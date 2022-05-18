
FROM python:3.10.4-alpine as base
FROM base as builder

COPY requirements.txt /requirements.txt
RUN pip install --user -r /requirements.txt

FROM base
WORKDIR /code

COPY --from=builder /root/.local /root/.local
COPY . .

VOLUME /data

ENV PATH=/root/.local:$PATH

CMD [ "python", "./main.py" ]
