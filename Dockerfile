# Menggunakan base image Python slim yang stabil dan efisien
FROM python:3.11-slim

# Mencegah pembuatan file .pyc dan memastikan output log unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Menetapkan direktori kerja container
WORKDIR /app

# Menyalin requirements.txt terlebih dahulu untuk memanfaatkan caching Docker layer
COPY requirements.txt .

# Menginstal seluruh dependensi tanpa menyimpan cache pip
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin kode aplikasi dashboard Streamlit
COPY app.py .

# Ekspos port default Streamlit
EXPOSE 8501

# Menjalankan Streamlit pada host 0.0.0.0 dan port 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
