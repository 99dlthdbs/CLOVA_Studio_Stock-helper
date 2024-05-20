FROM python:3.12

WORKDIR /code

COPY ./Pipfilee /code/Pipfile
COPY ./Pipfile.lock /code/Pipfile.lock

RUN pip install pipenv
RUN pipenv install
RUN pipenv shell

COPY . /code/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]