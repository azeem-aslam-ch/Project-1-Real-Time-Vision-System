FROM python:3.11-slim

WORKDIR /app

COPY streamlit_ui/requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

COPY . .

CMD ["streamlit", "run", "streamlit_ui/app.py", "--server.address=0.0.0.0"]
