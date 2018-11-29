ARG PLEX_VERSION=1.15.3.876-ad6e39743
FROM plexinc/pms-docker:${PLEX_VERSION}

# Upgrade system and install required packages
RUN apt-get update \
 && apt-get --no-install-recommends -y install \
      cron \
      fuse \
      gcc \
      libffi-dev \
      libfuse-dev \
      libssl-dev \
      locales \
      python-dev \
 # Clean up
 && apt-get -y autoremove \
 && apt-get -y clean \
 && rm -rf /tmp/* \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /var/tmp/*

# Ensure proper locale
RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG=en_US.utf8
ENV LANGUAGE=en_US.utf8
ENV LC_ALL=en_US.utf8

# Environment
ENV GIMME_ARCH amd64
ENV GIMME_GO_VERSION 1.12.4
ENV GIMME_OS linux
ENV GIMME_ROOT /home/.gimme
ENV GOPATH /home/go
ENV GOROOT ${GIMME_ROOT}/versions/go${GIMME_GO_VERSION}.${GIMME_OS}.${GIMME_ARCH}
ENV PATH ${PATH}:${GOPATH}/bin:${GOROOT}/bin
ENV S6_VERSION v1.22.1.0
ENV STORAGE_UTIL_VERSION 4.38

# Temporarily overwrite HOME
ENV HOME /home

# Get newer S6 overlay
RUN curl -sSLO https://github.com/just-containers/s6-overlay/releases/download/${S6_VERSION}/s6-overlay-amd64.tar.gz \
 && curl -sSLO https://github.com/just-containers/s6-overlay/releases/download/${S6_VERSION}/s6-overlay-amd64.tar.gz.sig \
 # Verify S6 archive signature
 && curl https://keybase.io/justcontainers/key.asc | gpg --import \
 && gpg --verify s6-overlay-amd64.tar.gz.sig s6-overlay-amd64.tar.gz \
 # Upgrade done in 2 steps to avoid overriding the /bin -> /usr/bin symlink
 && tar xzf s6-overlay-amd64.tar.gz -C / --exclude="./bin" \
 && tar xzf s6-overlay-amd64.tar.gz -C /usr ./bin \
 # Clean up
 && rm s6-overlay-amd64.tar.gz \
 && rm s6-overlay-amd64.tar.gz.sig

# Install Git
RUN apt-get update \
 && apt-get --no-install-recommends -y install git \
 # Install Golang
 && curl -sSL https://raw.githubusercontent.com/travis-ci/gimme/master/gimme | bash \
 # Install Google Cloud Storage FUSE
 && go get -u github.com/googlecloudplatform/gcsfuse \
 # Clean up
 && apt-get remove -y git \
 && apt-get -y autoremove \
 && apt-get -y clean \
 && rm -rf /tmp/* \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /var/tmp/* \
 && rm -rf ${GIMME_ROOT} \
 && rm -rf ${GOPATH}/src/*

# Install pip
RUN curl -sSL https://raw.githubusercontent.com/pypa/get-pip/master/get-pip.py | python \
 # Install gsutil to manage Plex metadata/database snapshots
 && pip install gsutil==${STORAGE_UTIL_VERSION}

# Reset HOME https://github.com/plexinc/pms-docker/blob/155f00c71b50f94c73ffea0aae16cc61ef957df7/Dockerfile#L46
ENV HOME /config

COPY root /

ENTRYPOINT ["/init"]
