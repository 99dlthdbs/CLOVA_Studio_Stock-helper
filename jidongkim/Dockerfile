FROM python:3.12

WORKDIR /code

ENV PIPENV_VENV_IN_PROJECT=1

COPY ./Pipfile /code/Pipfile
COPY ./Pipfile.lock /code/Pipfile.lock

RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile

COPY . /code/

EXPOSE 8000

CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]