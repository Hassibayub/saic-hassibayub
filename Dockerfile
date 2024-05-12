FROM python:3.11-slim
WORKDIR /app

COPY . .
COPY .env .

#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

RUN apt update
RUN apt install sqlite3

# Load environment variables from .env file
RUN cat /app/.env | grep -v '#' | xargs -I {} echo export {} >> /root/.bashrc
ENV PYTHONPATH=/app

EXPOSE 8501
CMD ["streamlit", "run", "webapp/app.py", "--server.address", "0.0.0.0"]