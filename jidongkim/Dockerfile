FROM python:3.12

WORKDIR /code

COPY ./Pipfile /code/Pipfile
COPY ./Pipfile.lock /code/Pipfile.lock

RUN pip install pipenv
RUN pipenv install

COPY . /code/

EXPOSE 8000

CMD ["pipenv", "shell"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]