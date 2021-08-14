FROM python:3.8-slim
WORKDIR /NOSQLBACKEND
COPY . /NOSQLBACKEND
# to install the requirements
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 8000
RUN cd /usr/local/bin
CMD ["python3", "app.py"]