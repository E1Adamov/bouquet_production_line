FROM python

RUN mkdir -p /home/workspace/src
COPY ./requirements.txt /home/workspace/
RUN pip install -r /home/workspace/requirements.txt
COPY ./src /home/workspace/src
COPY ./run.py /home/workspace/run.py
COPY ./config.py /home/workspace/config.py

WORKDIR /home/workspace

CMD python run.py
