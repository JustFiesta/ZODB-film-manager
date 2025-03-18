FROM python:3.12 AS build
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN pyinstaller --onefile run.py

FROM python:3.12-slim
WORKDIR /app
COPY --from=build /app/dist/run /app
CMD ["./run"]
