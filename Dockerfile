
FROM python:3.10.4 as builder

COPY requirements.txt /requirements.txt
RUN pip install --user -r /requirements.txt

FROM python:3.10.4
WORKDIR /code

COPY --from=builder /root/.local /root/.local
COPY . .

VOLUME /data

ENV PATH=/root/.local:$PATH

CMD [ "python", "./main.py" ]
