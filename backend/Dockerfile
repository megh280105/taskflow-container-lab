FROM python:3.12-slim AS builder

ENV VENV_PATH=/opt/taskflow-venv
ENV PATH="${VENV_PATH}/bin:${PATH}"

RUN python -m venv "${VENV_PATH}"

WORKDIR /app

COPY pyproject.toml ./
COPY app ./app
COPY worker.py ./worker.py

RUN pip install --upgrade pip && pip install .


FROM python:3.12-slim AS runtime

ENV VENV_PATH=/opt/taskflow-venv
ENV PATH="${VENV_PATH}/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

COPY --from=builder "${VENV_PATH}" "${VENV_PATH}"
COPY app ./app
COPY worker.py ./worker.py

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
