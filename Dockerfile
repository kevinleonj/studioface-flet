FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir flet>=0.25.0 httpx python-dotenv Pillow
COPY . .
ENV FLET_FORCE_WEB_SERVER=true
ENV FLET_SERVER_PORT=8080
ENV FLET_WEB_RENDERER=canvaskit
EXPOSE 8080
CMD ["python", "app/main.py"]
