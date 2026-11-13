FROM python:3.10-slim-buster

RUN python -m pip install --upgrade pip
RUN pip install pipenv
WORKDIR /home
COPY bot .
RUN pipenv install -r requirements.txt
RUN pipenv run pip install --force-reinstall "setuptools==80.9.0"
CMD [ "pipenv", "run", "python", "main.py" ]