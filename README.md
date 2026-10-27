# 🌐 GDELT_BigData: Pipeline Data Engineering & Analytics

Proyek data engineering berskala besar untuk melakukan agregasi, penyimpanan analitik latensi rendah, serta visualisasi peristiwa global secara real-time berbasis data **GDELT (Global Database of Events, Language, and Tone)**.

Arsitektur sistem dibangun dengan prinsip *Speed Layer* (DuckDB) untuk analitik interaktif, *Serving/Presentation Layer* (Streamlit & Plotly), serta dirancang untuk integrasi masa depan dengan *Batch Layer* (Apache Spark / PySpark) dan kontainerisasi menggunakan Docker.

---

## 🏛️ Arsitektur Sistem

```text
[ GDELT 2.0 Global Feeds ] (Update setiap 15 Menit)
            │
            ▼
[ Ingestion Pipeline ] ──► [ Raw Storage / Parquet Archives ]
            │
            ▼
    [ DuckDB Speed Layer ] (gdelt.db)
     ├── gdelt_events (21k+ records, skema analitik terindeks)
     └── pipeline_logs (monitoring status, latensi, metrik baris)
            │
            ▼
[ Streamlit Interactive Dashboard ] (app.py)
 ├── Metrik Real-Time & Monitoring Pipeline
 ├── Distribusi Kategori Peristiwa (QuadClass)
 ├── Analisis Top Negara Aktor Utama
 ├── Peta Persebaran Geografis Global (Plotly scatter_geo)
 └── Mesin Pencari Peristiwa & Sumber Berita
```

---

## 📁 Struktur Direktori

```text
GDELT_BigData/
├── app.py                  # Aplikasi dashboard Streamlit (mendukung DB_PATH dinamis)
├── gdelt.db                # Database lokal DuckDB (Speed/Serving Layer)
├── gdelt_clean.csv         # Snapshot dataset bersih yang diekspor
├── processed_urls.txt      # Log checkpoint batch URL GDELT yang telah diproses
├── requirements.txt        # Daftar dependensi Python terverifikasi
├── .gitignore              # Pengecualian file binary, DB, dan cache dari git
├── README.md               # Dokumentasi teknis proyek
├── analytics/              # File laporan analitik dan audit data
│   └── charts/             # Visualisasi statis (.png)
└── raw_data/               # Arsip file mentah GDELT (.export.CSV & .zip)
```

---

## 🗄️ Skema Database (`gdelt.db`)

Database DuckDB menggunakan dua tabel utama:

1. **`gdelt_events`**: Menyimpan data peristiwa GDELT yang telah dinormalisasi.
   * `GLOBALEVENTID`: ID unik peristiwa global.
   * `SQLDATE`, `MonthYear`, `Year`: Metadata penanggalan peristiwa.
   * `Actor1*` & `Actor2*`: Data aktor (nama, kode negara, etnis, agama, peran).
   * `EventCode`, `QuadClass`, `GoldsteinScale`: Klasifikasi konflik/kerjasama dan skala dampak.
   * `NumMentions`, `NumSources`, `NumArticles`, `AvgTone`: Metrik atensi media dan sentimen.
   * `ActionGeo_*`: Lokasi geografis (nama wilayah, negara, koordinat Lat/Long).
   * Kolom fitur tambahan: `DATEADDED_datetime`, `SQLDATE_datetime`, `EventCategory`, `EventDate`.

2. **`pipeline_logs`**: Menyimpan histori operasional ingestion.
   * `log_id`, `execution_time`: Identitas dan waktu proses pipeline.
   * `status`: Status eksekusi (`SUCCESS`, `FAILED`, dsb.).
   * `fetched_rows`, `inserted_rows`, `duplicate_rows`: Metrik volume data.
   * `data_latency_minutes`: Latensi antara waktu rilis data GDELT dengan waktu masuk database.
   * `error_message`: Pesan kesalahan jika terjadi kegagalan.

---

## 🚀 Panduan Memulai (Pengembangan Lokal)

### 1. Prasyarat
* Python 3.10+ (disarankan menggunakan Python 3.11 atau 3.12).

### 2. Persiapan Virtual Environment
```bash
# Membuat virtual environment
python -m venv .venv

# Aktivasi virtual environment:
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate
```

### 3. Instalasi Dependensi
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Database (`DB_PATH`)
Aplikasi `app.py` dirancang untuk membaca path database secara dinamis melalui environment variable `DB_PATH`. Jika variabel tidak disetel, aplikasi akan otomatis menggunakan file `gdelt.db` pada direktori proyek.

* **Default (Lokal)**: Tidak perlu menyetel variabel jika `gdelt.db` berada di folder yang sama dengan `app.py`.
* **Kustom (Windows PowerShell)**:
  ```powershell
  $env:DB_PATH = "C:\path\to\gdelt.db"
  streamlit run app.py
  ```
* **Kustom (Linux/Bash)**:
  ```bash
  export DB_PATH="/path/to/gdelt.db"
  streamlit run app.py
  ```

### 5. Menjalankan Dashboard
```bash
streamlit run app.py
```
Buka browser pada alamat `http://localhost:8501`.

---

## 🐳 Kompatibilitas Docker (Rencana Mendatang)

Dashboard telah siap untuk dijalankan dalam container Docker dengan konfigurasi bind mount database:
```bash
# Contoh skenario container dengan bind mount
docker run -d -p 8501:8501 \
  -e DB_PATH=/app/data/gdelt.db \
  -v ${PWD}/gdelt.db:/app/data/gdelt.db:ro \
  gdelt-dashboard
```
*Catatan: Dashboard selalu membuka koneksi DuckDB dalam mode `read_only=True` guna mencegah benturan locking saat pipeline ingestion berjalan bersamaan.*

---

## 🗺️ Roadmap Tahapan Berikutnya
* [ ] **Tahap Dockerisasi**: Pembuatan `Dockerfile` dan `compose.yaml` untuk mengorkestrasi service Streamlit UI.
* [ ] **Tahap Standarisasi Pipeline Ingestion**: Mengintegrasikan skrip pengunduh otomatis batch 15-menit GDELT.
* [ ] **Tahap Integrasi PySpark**: Pemrosesan batch berskala besar untuk transformasi histori data tahunan, agregasi metrik sentimen, dan penyimpanan Parquet terpartisi.
