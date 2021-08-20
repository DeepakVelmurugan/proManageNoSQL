FROM python:3.8-slim
WORKDIR /NOSQLBACKEND
COPY . /NOSQLBACKEND
# to install the requirements
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 8000
RUN cd /usr/local/bin
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
CMD echo $AWS_ACCESS_KEY_ID
CMD echo $AWS_SECRET_ACCESS_KEY
CMD ["python3", "app.py"]