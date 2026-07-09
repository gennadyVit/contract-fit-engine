FROM python:3.11-slim

WORKDIR /app

COPY requirements-streamlit.txt .
RUN pip install --no-cache-dir -r requirements-streamlit.txt

COPY streamlit/ ./streamlit/

EXPOSE 8000

CMD ["streamlit", "run", "streamlit/app.py", \
     "--server.port", "8000", \
     "--server.address", "0.0.0.0", \
     "--server.headless", "true"]
