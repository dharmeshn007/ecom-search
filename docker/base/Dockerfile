FROM python:3.8.2

RUN apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install -y libmariadbclient-dev && \
    apt-get install -y gdal-bin && \
    apt-get install -y python3-dev

RUN groupadd --gid 1000 app && \
    useradd --gid 1000 --uid 1000 --no-create-home app

RUN set -eux; \
	apt-get --allow-releaseinfo-change update; \
	apt-get install -y gosu; \
	rm -rf /var/lib/apt/lists/*; \
    # verify that the binary works
	gosu nobody true

RUN python3 -m venv /appenv && \
	. /appenv/bin/activate && \
	pip install pip --upgrade

RUN . /appenv/bin/activate

ENV PATH="/appenv/bin:$PATH"

RUN pip3 install https://download.pytorch.org/whl/cpu/torch-1.13.1%2Bcpu-cp38-cp38-linux_x86_64.whl

RUN pip3 install torchvision

COPY requirements.txt /requirements.txt

RUN pip install -r requirements.txt --use-pep517

RUN  . /appenv/bin/activate && python -c 'from sentence_transformers import SentenceTransformer;SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")'

