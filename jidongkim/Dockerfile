FROM python:3.12.3

WORKDIR /code

ENV PIPENV_VENV_IN_PROJECT=1

RUN pip install pipenv

COPY ./Pipfile .
COPY ./Pipfile.lock .

RUN pipenv install --deploy --ignore-pipfile

COPY . .

EXPOSE 8000

CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]