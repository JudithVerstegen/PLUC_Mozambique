FROM python:2.7-wheezy
MAINTAINER Daniel Nüst <daniel.nuest@uni-muenster.de>

ENV PCRASTER_VERSION=4.1.0
ENV PCRASTER_ARCH=_x86-64

# Prerequisites > http://pcraster.geo.uu.nl/getting-started/pcraster-on-linux/prerequisites/
RUN apt-get update \ 
  && apt-get install -y --no-install-recommends \
    python-numpy \
    lsb \
    libjpeg62

# http://pcraster.geo.uu.nl/getting-started/pcraster-on-linux/installation-linux/
WORKDIR /opt
RUN curl -LO https://downloads.sourceforge.net/project/pcraster/PCRaster/$PCRASTER_VERSION/pcraster-$PCRASTER_VERSION$PCRASTER_ARCH.tar.gz \
  && mkdir pcraster \
  && tar zxf pcraster-*.tar.gz --strip-components=1 -C pcraster

ENV PATH=/opt/pcraster/bin:$PATH
ENV PYTHONPATH=/opt/pcraster/python:$PYTHONPATH

ENTRYPOINT ["pcrcalc"]

# docker build --tag pcraster-pluc .
#
# docker run -it --rm pcraster-pluc p