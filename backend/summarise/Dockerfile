FROM python:3.10.12

RUN mkdir api

WORKDIR /api

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . /api/

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000" ]