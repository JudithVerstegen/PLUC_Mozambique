FROM python:2.7

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
COPY README.md README.md

ARG VERSION=dev
ARG VCS_URL
ARG VCS_REF
ARG BUILD_DATE

# Metadata http://label-schema.org/rc1/
LABEL maintainer="Daniel Nüst <daniel.nuest@uni-muenster.de>"
      org.label-schema.vendor="Judith Verstegen, Daniel Nüst" \
      org.label-schema.url="http://o2r.info" \
      org.label-schema.name="PLUC Mozambique" \
      org.label-schema.description="PCRaster Land Use Change model (PLUC) for Mozambique, created in PCRaster (http://pcraster.geo.uu.nl/) in Python. \
      Results of the model are published in Verstegen et al. 2012 and van der Hilst et al. 2012." \
      org.label-schema.usage="/pluc/README.md" \
      org.label-schema.version=$VERSION \
      org.label-schema.vcs-url=$VCS_URL \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.schema-version="rc1" \
      org.label-schema.docker.cmd="docker run -it --name lu-moz pcraster-pluc"

ENTRYPOINT ["python"]
CMD ["LU_Moz.py"]
