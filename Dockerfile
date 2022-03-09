# Prepare the building platform
FROM debian:stretch-slim AS builder
# Warning: the next line will be cached. If any new package will be needed in the future, this will have to be changed.
RUN apt-get update
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        make \
        libc6-dev \
        libglib2.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Build naken-asm
FROM builder AS naken_builder
WORKDIR /naken_asm
COPY naken_asm .
RUN bash configure --enable-msp430
RUN make

# Build msp430-emu-uctf
FROM builder AS emulator_builder
WORKDIR /msp430-emu-uctf
COPY msp430-emu-uctf .
RUN make msp430-emu

# The app!
FROM python:3.7-slim-stretch
RUN apt-get update && apt-get install -y --no-install-recommends \
        gdb-msp430 \
        libglib2.0 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=naken_builder /naken_asm/naken_asm /bin
COPY --from=naken_builder /naken_asm/naken_util /bin
COPY --from=emulator_builder /msp430-emu-uctf/msp430-emu /bin

WORKDIR /app
COPY app .
RUN pip install -e . gunicorn tox

CMD gunicorn --bind=0.0.0.0:$PORT microserver.views:app --threads=32 --access-logfile=- --access-logformat="%(t)s %(h)s %(l)s %(r)s %(l)s %(s)s (%(B)s)"