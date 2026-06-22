# Single-stage image for local development / docker-compose.
# CI uses the split Dockerfile-base-image + Dockerfile-to-deploy for caching.
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /autotester

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# The runner uses channel='chrome' (real Chrome), which is not bundled in the base image.
RUN python -m playwright install --with-deps chrome

COPY . .

EXPOSE 8080
ENTRYPOINT ["python", "main.py"]
CMD ["gui", "--host", "0.0.0.0", "--port", "8080"]
