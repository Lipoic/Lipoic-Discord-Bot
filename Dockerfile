
FROM python:3.10.4-alpine as base
FROM base as builder

COPY requirements.txt /requirements.txt
RUN pip3 install --user -r /requirements.txt

FROM base
WORKDIR /code

COPY --from=builder /root/.local /root/.local
COPY ./lipoic ./lipoic

ENV PATH=/root/.local:$PATH

CMD [ "python", "-m", "lipoic" ]
