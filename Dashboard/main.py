import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



# Load Data
df = pd.read_csv("cleaned_main_data.csv", parse_dates=["order_purchase_timestamp", "order_delivered_customer_date"])

# Sidebar untuk Navigasi
st.sidebar.title("📊 Dashboard E-Commerce")
menu = st.sidebar.radio("🔍 Pilih Analisis", [
    "Pola Pembelian Pelanggan", 
    "Efektivitas Pengiriman", 
    "Distribusi Pesanan per Kategori", 
    "Metode Pembayaran",
    "RFM Analysis"])

# Pola Pembelian Pelanggan
if menu == "Pola Pembelian Pelanggan":
    st.title("📅 Pola Pembelian Pelanggan Berdasarkan Waktu")
    
    # Date Range Picker
    start_date = st.sidebar.date_input("Start Date", df["order_purchase_timestamp"].min().date())
    end_date = st.sidebar.date_input("End Date", df["order_purchase_timestamp"].max().date())
    
    df_filtered = df[(df["order_purchase_timestamp"].dt.date >= start_date) & (df["order_purchase_timestamp"].dt.date <= end_date)]
    
    df_filtered["order_month"] = df_filtered["order_purchase_timestamp"].dt.to_period("M")
    orders_per_month = df_filtered.groupby("order_month").size()
    
    st.subheader("📈 Jumlah Pesanan per Bulan")
    fig, ax = plt.subplots(figsize=(8, 4))
    orders_per_month.plot(ax=ax, marker="o", color='b')
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Jumlah Pesanan")
    st.pyplot(fig)
    
    df_filtered["order_day"] = df_filtered["order_purchase_timestamp"].dt.day_name()
    orders_per_day = df_filtered["order_day"].value_counts()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Jumlah Pesanan per Hari")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=orders_per_day.index, y=orders_per_day.values, ax=ax, palette="coolwarm")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        st.pyplot(fig)
    
    with col2:
        df_filtered["order_hour"] = df_filtered["order_purchase_timestamp"].dt.hour
        st.subheader("⏰ Distribusi Waktu Pemesanan")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(df_filtered["order_hour"], bins=24, kde=True, color='g', ax=ax)
        st.pyplot(fig)
    
    # Visualisasi Daily Orders
    df_filtered["order_date"] = df_filtered["order_purchase_timestamp"].dt.date
    daily_orders = df_filtered.groupby("order_date").size()
    
    st.subheader("📅 Jumlah Pesanan Harian")
    fig, ax = plt.subplots(figsize=(10, 5))
    daily_orders.plot(ax=ax, color='purple')
    ax.set_xlabel("Tanggal")
    ax.set_ylabel("Jumlah Pesanan")
    st.pyplot(fig)

# Efektivitas Pengiriman
elif menu == "Efektivitas Pengiriman":
    st.title("🚚 Efektivitas Pengiriman Barang")
    df["delivery_time"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📌 Rata-rata Waktu Pengiriman")
        st.metric(label="Rata-rata Pengiriman", value=f"{df['delivery_time'].mean():.2f} hari")
    
    with col2:
        st.subheader("📊 Distribusi Waktu Pengiriman")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(df["delivery_time"].dropna(), bins=20, kde=True, color='r', ax=ax)
        st.pyplot(fig)

# Distribusi Pesanan Berdasarkan Kategori Produk
elif menu == "Distribusi Pesanan per Kategori":
    st.title("📦 Distribusi Pesanan Berdasarkan Kategori Produk")
    
    category_counts = df["product_category_name"].value_counts()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 Kategori Produk Terpopuler")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=category_counts[:10].index, y=category_counts[:10].values, ax=ax, palette="viridis")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        st.pyplot(fig)
    
    with col2:
        st.subheader("📊 Distribusi Pesanan (Pie Chart)")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(category_counts[:10], labels=category_counts[:10].index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
        ax.axis("equal")
        st.pyplot(fig)

# Metode Pembayaran dan Jumlah Transaksi
elif menu == "Metode Pembayaran":
    st.title("💳 Hubungan Metode Pembayaran dan Jumlah Transaksi")
    
    payment_counts = df["payment_type"].value_counts()
    
    st.subheader("📊 Distribusi Metode Pembayaran")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x=payment_counts.index, y=payment_counts.values, ax=ax, palette="Blues")
    st.pyplot(fig)

# RFM Analysis
elif menu == "RFM Analysis":
    st.title("📊 RFM Analysis")
    reference_date = df["order_purchase_timestamp"].max()
    rfm_df = df.groupby("customer_id").agg({
        "order_purchase_timestamp": lambda x: (reference_date - x.max()).days,
        "order_id": "count",
        "payment_value": "sum"
    }).rename(columns={"order_purchase_timestamp": "Recency", "order_id": "Frequency", "payment_value": "Monetary"})
    
    st.subheader("📋 Hasil RFM Analysis")
    st.dataframe(rfm_df.sort_values(by=["Recency", "Frequency", "Monetary"], ascending=[True, False, False]))