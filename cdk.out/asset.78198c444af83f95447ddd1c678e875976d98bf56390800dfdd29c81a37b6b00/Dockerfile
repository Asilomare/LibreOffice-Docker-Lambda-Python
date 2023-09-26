FROM amazon/aws-lambda-python:3.9

RUN pip install brotlipy && \
    pip install boto3

COPY fonts.conf /var/task/fonts/fonts.conf
COPY lo.tar.br /opt/
COPY script.py ./
COPY lo_loader.py ./

CMD ["script.docToPdf"]
