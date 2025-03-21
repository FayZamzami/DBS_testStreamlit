import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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



# Daily Orders
st.subheader("📅 Daily Orders")
daily_orders = filtered_df.groupby(filtered_df['order_purchase_timestamp'].dt.date).agg({
    'order_id': 'count',
    'payment_value': 'sum'
}).reset_index()
daily_orders.columns = ['Tanggal', 'Jumlah Order', 'Total Revenue']

fig, ax1 = plt.subplots(figsize=(10, 5))
ax2 = ax1.twinx()

ax1.bar(daily_orders['Tanggal'], daily_orders['Jumlah Order'], color='blue', label='Jumlah Order', alpha=0.6)
ax2.plot(daily_orders['Tanggal'], daily_orders['Total Revenue'], color='red', marker='o', linestyle='-', label='Total Revenue')

ax1.set_xlabel('Tanggal')
ax1.set_ylabel('Jumlah Order', color='blue')
ax2.set_ylabel('Total Revenue (USD)', color='red')
ax1.set_title('Jumlah Order Harian dan Total Revenue')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

st.pyplot(fig)

# Best Performing Products
st.subheader("🏆 Best Performing Products")
best_products = filtered_df['product_id'].value_counts().nlargest(10)
fig, ax = plt.subplots()
best_products.plot(kind='bar', ax=ax, color='skyblue')
ax.set_title('Top 10 Best Performing Products')
ax.set_xlabel('Product ID')
ax.set_ylabel('Total Orders')
st.pyplot(fig)

# Worst Performing Products
st.subheader("❌ Worst Performing Products")
worst_products = filtered_df['product_id'].value_counts().nsmallest(10)
fig, ax = plt.subplots()
worst_products.plot(kind='bar', ax=ax, color='salmon')
ax.set_title('Top 10 Worst Performing Products')
ax.set_xlabel('Product ID')
ax.set_ylabel('Total Orders')
st.pyplot(fig)

# RFM Analysis
st.subheader("📊 RFM Analysis")
df['recency'] = (df['order_purchase_timestamp'].max() - df['order_purchase_timestamp']).dt.days
rfm = df.groupby('customer_id').agg({
    'recency': 'min',
    'order_id': 'count',
    'payment_value': 'sum'
}).reset_index()

rfm.columns = ['Customer ID', 'Recency', 'Frequency', 'Monetary']
fig, ax = plt.subplots()
sns.scatterplot(data=rfm, x='Recency', y='Monetary', size='Frequency', hue='Frequency', ax=ax)
ax.set_title('RFM Analysis')
st.pyplot(fig)

rfm_data = filtered_df.groupby("customer_id").agg({
    "order_purchase_timestamp": lambda x: (df["order_purchase_timestamp"].max() - x.max()).days,
    "order_id": "count",
    "payment_value": "sum"
}).reset_index()
rfm_data.columns = ["customer_id", "recency", "frequency", "monetary"]
st.dataframe(rfm_data)

# Best Customers Based on RFM
st.subheader("🌟 Best Customers Based on RFM Parameters")
best_customers = rfm_data.nlargest(10, 'monetary')
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=best_customers, x='customer_id', y='monetary', ax=ax, palette='coolwarm')
ax.set_title('Top 10 Best Customers by Monetary Value')
ax.set_xlabel("Customer ID")
ax.set_ylabel("Monetary")
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
st.pyplot(fig)

# Grafik Distribusi Pesanan per Kategori Produk
st.subheader("📦 Distribusi Jumlah Pesanan Berdasarkan Kategori Produk")
category_counts = filtered_df["product_category_name"].value_counts().reset_index()
category_counts.columns = ["Kategori Produk", "Jumlah Pesanan"]
fig, ax = plt.subplots(figsize=(14, 7))
sns.barplot(data=category_counts, x='Kategori Produk', y='Jumlah Pesanan', color='purple')
ax.set_title("Distribusi Pesanan per Kategori")
ax.set_xlabel("Kategori Produk")
ax.set_ylabel("Jumlah Pesanan")
plt.xticks(rotation=90)
st.pyplot(fig)

# Hubungan Metode Pembayaran dan Jumlah Transaksi
st.subheader("💳 Hubungan Metode Pembayaran dan Jumlah Transaksi")
payment_counts = filtered_df["payment_type"].value_counts().reset_index()
payment_counts.columns = ["Metode Pembayaran", "Jumlah Transaksi"]

fig, ax = plt.subplots()
ax.pie(payment_counts["Jumlah Transaksi"], labels=payment_counts["Metode Pembayaran"], autopct='%1.1f%%', colors=sns.color_palette("Set2"))
ax.set_title("Distribusi Metode Pembayaran")
st.pyplot(fig)

# Persebaran Pelanggan Berdasarkan Kota & Negara Bagian
st.subheader("🏙️ Persebaran Pelanggan Berdasarkan Kota & Negara Bagian")
city_counts = filtered_df["customer_city"].value_counts().reset_index()
city_counts.columns = ["Kota", "Jumlah Pelanggan"]
city_counts = city_counts.nlargest(10, "Jumlah Pelanggan")

fig, ax = plt.subplots(figsize=(14, 7))
sns.barplot(data=city_counts, x='Kota', y='Jumlah Pelanggan', palette='Greens_r')
ax.set_title("Top 10 Kota dengan Jumlah Pelanggan Terbanyak")
ax.set_xlabel("Kota")
ax.set_ylabel("Jumlah Pelanggan")
plt.xticks(rotation=45, ha='right')
st.pyplot(fig)

# Hubungan Harga Produk dan Biaya Pengiriman
st.subheader("📈 Hubungan Harga Produk dan Biaya Pengiriman")

            #    Batasi jumlah kategori untuk menjaga keterbacaan
top_categories = filtered_df["product_category_name"].value_counts().index[:15]  # Ambil 15 kategori teratas
filtered_data = filtered_df[filtered_df["product_category_name"].isin(top_categories)]

fig, ax = plt.subplots(figsize=(10, 6))
scatter = sns.scatterplot(
    data=filtered_data, x="price", y="freight_value", hue="product_category_name",
    alpha=0.7, edgecolor=None, palette="tab10"
)

ax.set_title("Hubungan antara Harga Produk dan Biaya Pengiriman", fontsize=12)
ax.set_xlabel("Harga Produk (USD)", fontsize=10)
ax.set_ylabel("Biaya Pengiriman (USD)", fontsize=10)

            # Pisahkan legenda agar tidak menumpuk di dalam grafik
legend_labels, _ = scatter.get_legend_handles_labels()
fig_leg, ax_leg = plt.subplots(figsize=(3, 6))
ax_leg.legend(legend_labels, top_categories, title="Kategori Produk", loc="center")
ax_leg.axis("off")  # Hilangkan sumbu pada legenda

st.pyplot(fig)
st.pyplot(fig_leg)

# Informasi Penjualan Berdasarkan Kategori Produk
st.subheader("📊 Informasi Penjualan Berdasarkan Kategori Produk")
sales_data = filtered_df.groupby("product_category_name")["payment_value"].sum().sort_values(ascending=False).head(20)
fig, ax = plt.subplots(figsize=(14, 7))
sales_data.plot(kind='bar', ax=ax, color='blue')
ax.set_title("Total Pendapatan per Kategori Produk")
ax.set_xlabel("Kategori Produk")
ax.set_ylabel("Total Pendapatan (USD)")
plt.xticks(rotation=45, ha='right')
st.pyplot(fig)

# Jumlah Cicilan Masing-Masing Pelanggan
st.subheader("💰 Jumlah Cicilan Masing-Masing Pelanggan")
fig, ax = plt.subplots()
sns.histplot(filtered_df["payment_installments"], bins=30, kde=True, color='indianred', ax=ax)
ax.set_title("Distribusi Cicilan Masing-Masing Pelanggan")
st.pyplot(fig)

# Produk yang Paling Banyak Dicicil
st.subheader("🛒 Produk yang Paling Banyak Dicicil")
product_installments = filtered_df.groupby("product_id")["payment_installments"].sum().nlargest(10)
fig, ax = plt.subplots()
product_installments.plot(kind='bar', ax=ax, color='orange')
ax.set_title("Top 10 Produk dengan Cicilan Terbanyak")
ax.set_xlabel("Product ID")
ax.set_ylabel("Total Cicilan")
st.pyplot(fig)


# Copyright Footer
st.markdown("---")
st.markdown("© 2025 by FayadhRizqiZamzami")
