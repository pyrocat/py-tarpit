FROM python:3.10-slim-bookworm as venv_builder

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt  ./

RUN mkdir $VIRTUAL_ENV && \
    chown 1000:1000 $VIRTUAL_ENV && \
    python -m venv $VIRTUAL_ENV && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm -rf /var/cache/apt/* /var/lib/apt/lists/*


FROM venv_builder as app

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN useradd -Um -u 1000 --shell /bin/bash app_user

USER app_user

WORKDIR /home/app_user/tarpit/

COPY --link --from=venv_builder --chown=app_user:app_user $VIRTUAL_ENV $VIRTUAL_ENV

COPY py_tarpit/ py_tarpit/

EXPOSE 8080
ENTRYPOINT ["python", "py_tarpit/main.py"]