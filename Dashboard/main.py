import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Load dataset
DATA_PATH = "./Dashboard/cleaned_main_data.csv"
df = pd.read_csv(DATA_PATH, parse_dates=[
    "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
    "order_delivered_customer_date", "order_estimated_delivery_date"
])

# Sidebar Filters
st.sidebar.header("\U0001F50D Opsi Eksplorasi Data")

# Date Range Filter
st.sidebar.subheader("Date Range")
min_date = df["order_purchase_timestamp"].min().date()
max_date = df["order_purchase_timestamp"].max().date()

start_date = st.sidebar.text_input("Start Date", "2016/01/01")
end_date = st.sidebar.text_input("End Date", "2018/12/31")

# Convert string dates to datetime objects
try:
    start_date = datetime.strptime(start_date, "%Y/%m/%d").date()
    end_date = datetime.strptime(end_date, "%Y/%m/%d").date()
except ValueError:
    st.sidebar.warning("Please use format YYYY/MM/DD for dates")
    start_date = min_date
    end_date = max_date

# Existing category and payment filters
selected_category = st.sidebar.selectbox("Pilih Kategori Produk:", ["Semua"] + sorted(df["product_category_name"].dropna().unique().tolist()))
selected_payment = st.sidebar.selectbox("Pilih Metode Pembayaran:", ["Semua"] + sorted(df["payment_type"].dropna().unique().tolist()))

# Filter Data
filtered_df = df.copy()

# Apply date filter
filtered_df = filtered_df[(filtered_df["order_purchase_timestamp"].dt.date >= start_date) & 
                          (filtered_df["order_purchase_timestamp"].dt.date <= end_date)]

# Apply existing filters
if selected_category != "Semua":
    filtered_df = filtered_df[filtered_df["product_category_name"] == selected_category]
if selected_payment != "Semua":
    filtered_df = filtered_df[filtered_df["payment_type"] == selected_payment]

# Judul Dashboard
st.title("📊 Dashboard E-Commerce Analysis")

# Statistik
col1, col2 = st.columns(2)
col1.metric("Total Orders", f"{filtered_df['order_id'].nunique():,}")
col2.metric("Total Revenue", f"${filtered_df['payment_value'].sum():,.2f}")

# Menampilkan Gambar yang Diupload
st.subheader("🖼️ Gambar yang Diupload")
uploaded_files = ["image.png"]  # Nama file yang telah diunggah
for file in uploaded_files:
    if os.path.exists(file):
        st.image(file, caption=f"Gambar: {file}", use_column_width=True)

# Daily Orders
st.subheader("📅 Daily Orders")
daily_orders = filtered_df.groupby(filtered_df['order_purchase_timestamp'].dt.date).size().reset_index(name='Jumlah Order')
fig_daily = px.line(daily_orders, x='order_purchase_timestamp', y='Jumlah Order', title='Daily Orders Over Time')
st.plotly_chart(fig_daily)

# Best Performing Products
st.subheader("🏆 Best Performing Products")
best_products = filtered_df['product_id'].value_counts().nlargest(10).reset_index()
best_products.columns = ['Product ID', 'Total Orders']
fig_best = px.bar(best_products, x='Product ID', y='Total Orders', color='Product ID', title='Top 10 Best Performing Products')
st.plotly_chart(fig_best)

# Worst Performing Products
st.subheader("❌ Worst Performing Products")
worst_products = filtered_df['product_id'].value_counts().nsmallest(10).reset_index()
worst_products.columns = ['Product ID', 'Total Orders']
fig_worst = px.bar(worst_products, x='Product ID', y='Total Orders', color='Product ID', title='Top 10 Worst Performing Products')
st.plotly_chart(fig_worst)

# RFM Analysis
st.subheader("📊 RFM Analysis")
df['recency'] = (df['order_purchase_timestamp'].max() - df['order_purchase_timestamp']).dt.days
rfm = df.groupby('customer_id').agg({
    'recency': 'min',
    'order_id': 'count',
    'payment_value': 'sum'
}).reset_index()
rfm.columns = ['Customer ID', 'Recency', 'Frequency', 'Monetary']
fig_rfm = px.scatter(rfm, x='Recency', y='Monetary', size='Frequency', color='Frequency', title='RFM Analysis')
st.plotly_chart(fig_rfm)

# Best Customers Based on RFM
st.subheader("🌟 Best Customers Based on RFM Parameters")
best_customers = rfm.nlargest(10, 'Monetary')
fig_best_customers = px.bar(best_customers, x='Customer ID', y='Monetary', color='Customer ID', title='Top 10 Best Customers by Monetary Value')
st.plotly_chart(fig_best_customers)

# Grafik Distribusi Pesanan per Kategori Produk
st.subheader("📦 Distribusi Jumlah Pesanan Berdasarkan Kategori Produk")
category_counts = filtered_df["product_category_name"].value_counts().reset_index()
category_counts.columns = ["Kategori Produk", "Jumlah Pesanan"]
fig1 = px.bar(category_counts, x="Kategori Produk", y="Jumlah Pesanan", color="Kategori Produk",
              title="Distribusi Pesanan per Kategori", labels={"Jumlah Pesanan": "Total Orders"})
st.plotly_chart(fig1)

# Grafik Hubungan Metode Pembayaran dan Jumlah Transaksi
st.subheader("💳 Hubungan Metode Pembayaran dan Jumlah Transaksi")
payment_counts = filtered_df["payment_type"].value_counts().reset_index()
payment_counts.columns = ["Metode Pembayaran", "Jumlah Transaksi"]
fig2 = px.pie(payment_counts, names="Metode Pembayaran", values="Jumlah Transaksi",
              title="Distribusi Metode Pembayaran", color_discrete_sequence=px.colors.qualitative.Set2)
st.plotly_chart(fig2)

# Persebaran Pelanggan Berdasarkan Kota & Negara Bagian
st.subheader("🏙️ Persebaran Pelanggan Berdasarkan Kota & Negara Bagian")
city_counts = filtered_df["customer_city"].value_counts().reset_index()
city_counts.columns = ["Kota", "Jumlah Pelanggan"]
fig3 = px.bar(city_counts.head(10), x="Kota", y="Jumlah Pelanggan", color="Kota",
              title="Top 10 Kota dengan Jumlah Pelanggan Terbanyak")
st.plotly_chart(fig3)

# Hubungan Harga Produk dan Biaya Pengiriman
st.subheader("📈 Hubungan Harga Produk dan Biaya Pengiriman")
fig4 = px.scatter(filtered_df, x="price", y="freight_value", color="product_category_name",
                  title="Hubungan antara Harga Produk dan Biaya Pengiriman",
                  labels={"price": "Harga Produk", "freight_value": "Biaya Pengiriman"})
st.plotly_chart(fig4)

# Informasi Penjualan Berdasarkan Kategori Produk
st.subheader("📊 Informasi Penjualan Berdasarkan Kategori Produk")
sales_data = filtered_df.groupby("product_category_name")["payment_value"].sum().reset_index()
fig5 = px.bar(sales_data, x="product_category_name", y="payment_value", color="product_category_name",
              title="Total Pendapatan per Kategori Produk", labels={"payment_value": "Total Pendapatan (USD)"})
st.plotly_chart(fig5)

# Jumlah Cicilan Masing-Masing Pelanggan
st.subheader("💰 Jumlah Cicilan Masing-Masing Pelanggan")
installments_data = filtered_df.groupby("customer_id")["payment_installments"].sum().reset_index()
fig6 = px.histogram(installments_data, x="payment_installments", nbins=30, color_discrete_sequence=["indianred"],
                    title="Distribusi Cicilan Masing-Masing Pelanggan")
st.plotly_chart(fig6)

# Produk yang Paling Banyak Dicicil
st.subheader("🛒 Produk yang Paling Banyak Dicicil")
product_installments = filtered_df.groupby("product_id")["payment_installments"].sum().reset_index()
top_products = product_installments.nlargest(10, "payment_installments")
fig7 = px.bar(top_products, x="product_id", y="payment_installments", color="product_id",
              title="Top 10 Produk dengan Cicilan Terbanyak")
st.plotly_chart(fig7)

# Copyright Footer
st.markdown("---")
st.markdown("© 2025 by FayadhRizqiZamzami")
