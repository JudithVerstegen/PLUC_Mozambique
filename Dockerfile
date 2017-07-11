FROM python:2.7-wheezy
MAINTAINER Daniel Nüst <daniel.nuest@uni-muenster.de>

ENV PCRASTER_VERSION=4.1.0
ENV PCRASTER_ARCH=_x86-64

# Prerequisites > http://pcraster.geo.uu.nl/getting-started/pcraster-on-linux/prerequisites/
RUN apt-get update \ 
  && apt-get install -y --force-yes --no-install-recommends \
    lsb \
    libjpeg62 \
    ffmpeg \
  && apt-get clean

RUN pip install numpy matplotlib

# http://pcraster.geo.uu.nl/getting-started/pcraster-on-linux/installation-linux/
WORKDIR /opt
RUN curl -LO https://downloads.sourceforge.net/project/pcraster/PCRaster/$PCRASTER_VERSION/pcraster-$PCRASTER_VERSION$PCRASTER_ARCH.tar.gz \
  && mkdir pcraster \
  && tar zxf pcraster-*.tar.gz --strip-components=1 -C pcraster \
  && rm pcraster-*.tar.gz

ENV PATH=/opt/pcraster/bin:$PATH
ENV PYTHONPATH=/opt/pcraster/python:$PYTHONPATH

LABEL name=PLUC_MOZAMBIQUE
LABEL version=1

WORKDIR /pluc
COPY model/ .

ENTRYPOINT ["python"]
CMD ["LU_Moz.py"]

### Reproduce with container:
#
## 1. Build Docker image
# $ docker build --tag pcraster-pluc .
#
## 2. Run Docker image
# $ docker run -it --name lu-moz pcraster-pluc
#
## 3. Extract videos from container
# $ docker cp lu-moz:/pluc/movie_euSc-ave.mp4 movie_euSc-ave.mp4
# $ docker cp lu-moz:/pluc/movie_landUse.mp4 movie_landUse.mp4
#
## 4. Run Docker image with own parameters
# $ docker run -it --rm -v $(pwd)/test/my_params.py:/pluc/Parameters.py pcraster-pluc
#
# Optional
# - linter: $ docker run -it --rm --privileged -v $(pwd):/root/ projectatomic/dockerfile-lint dockerfile_lint
# - bash inside container (for inspection, bugfixing): $ docker run -it --rm --entrypoint /bin/bash pcraster-pluc