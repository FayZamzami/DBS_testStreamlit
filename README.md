# E-Commerce Dashboard 📊

Dashboard interaktif menggunakan Streamlit untuk menganalisis pola pembelian, efektivitas pengiriman, distribusi pesanan, dan metode pembayaran pada dataset e-commerce.

---

## Setup Environment - Anaconda

Jika menggunakan Anaconda, jalankan perintah berikut:

```bash
conda create --name ecom-dash python=3.9
conda activate ecom-dash
pip install -r requirements.txt
```

---

## Setup Environment - Shell/Terminal

Jika menggunakan virtual environment dengan pipenv, jalankan perintah berikut:

```bash
mkdir ecom_dashboard
cd ecom_dashboard
pipenv install
pipenv shell
pip install -r requirements.txt
```

---

## Generate `requirements.txt`

Jika belum memiliki file `requirements.txt`, Anda bisa membuatnya dengan **pipreqs**:

```bash
pip install pipreqs
pipreqs . --force
```

---

## Run Streamlit App

Untuk menjalankan dashboard, pastikan Anda berada di dalam folder `Dashboard` lalu jalankan perintah:

```bash
cd Dashboard
streamlit run main.py
```

---

## Dataset

Dataset yang digunakan berasal dari **Brazilian E-Commerce Public Dataset by Olist** dan telah melalui tahap preprocessing.

- **Dataset utama (bersih)**: `Dashboard/cleaned_main_data.csv`
- **Dataset mentah**: `E_Commerce_Public_Dataset/`
  - `customers_dataset.csv`
  - `geolocation_dataset.csv`
  - `order_items_dataset.csv`
  - `order_payments_dataset.csv`
  - `order_reviews_dataset.csv`
  - `orders_dataset.csv`
  - `product_category_name_translation.csv`
  - `products_dataset.csv`
  - `sellers_dataset.csv`

---

## Notebook Analisis

Notebook eksplorasi dan analisis awal terdapat pada:

- `DBS_Proyek_Analisis_Data.ipynb`
