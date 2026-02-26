"""Streamlit dashboard for Monitoring Susenas."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.database import get_available_dates, init_db, read_data

TAHAPAN_ORDER = [
    "Pemutakhiran",
    "Pencacahan",
    "Pemeriksaan",
    "Pengiriman ke KabKota",
    "Penerimaan di KabKota",
    "Penerimaan di IPDS",
    "Pengolahan Dokumen K",
    "Pengolahan Dokumen KP",
]

st.set_page_config(
    page_title="Monitoring Susenas - Kalimantan Utara",
    page_icon=":bar_chart:",
    layout="wide",
)

st.title("Dashboard Monitoring Susenas Kalimantan Utara 2026")
st.caption("Menampilkan Persentase Belum Selesai dan Tingkat Error per Tahapan")

# Initialize DB (ensures table exists)
init_db()

# Sidebar - date filter
dates = get_available_dates()
if not dates:
    st.warning("Belum ada data. Jalankan ETL flow terlebih dahulu: `python -m src.etl_flow`")
    st.stop()

selected_date = st.sidebar.selectbox("Pilih Tanggal Scraping", dates)
df = read_data(scraped_date=selected_date)

if df.empty:
    st.info("Tidak ada data untuk tanggal yang dipilih.")
    st.stop()

# --- Subplot 4x2 Bar Chart ---
fig = make_subplots(
    rows=4,
    cols=2,
    subplot_titles=[f"{t}" for t in TAHAPAN_ORDER],
    vertical_spacing=0.08,
    horizontal_spacing=0.1,
)

for i, tahapan in enumerate(TAHAPAN_ORDER):
    df_tahap = df[df["tahapan"] == tahapan].copy()
    row = (i // 2) + 1
    col = (i % 2) + 1

    if df_tahap.empty:
        fig.add_annotation(
            text="Tidak ada data",
            row=row,
            col=col,
            showarrow=False,
        )
        continue

    df_tahap = df_tahap.sort_values("persentase", ascending=False)
    wilayah = df_tahap["wilayah"]
    nilai = df_tahap["persentase"]

    # Dynamic colors: red > 50%, yellow > 0%, green = 0%
    colors = [
        "#e74c3c" if v > 50 else "#f1c40f" if v > 0 else "#2ecc71" for v in nilai
    ]

    label_status = df_tahap["status"].iloc[0] if not df_tahap.empty else ""
    y_label = "Error (%)" if "Pengolahan" in tahapan else "Belum Selesai (%)"

    fig.add_trace(
        go.Bar(
            x=wilayah,
            y=nilai,
            name=tahapan,
            text=nilai.round(2).astype(str) + "%",
            textposition="auto",
            marker_color=colors,
            hovertemplate=f"Wilayah: %{{x}}<br>{label_status}: %{{y:.2f}}%<extra></extra>",
        ),
        row=row,
        col=col,
    )

    # Update subplot title with status label
    fig.layout.annotations[i].update(text=f"<b>{tahapan}</b><br>({label_status})")
    fig.update_yaxes(title_text=y_label, range=[0, 115], row=row, col=col)

fig.update_layout(
    height=1400,
    title_text=(
        "<b>Dashboard Monitoring Kendala Susenas</b>"
        "<br><sup>Belum Selesai & Error</sup>"
    ),
    title_x=0.5,
    showlegend=False,
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True)

# --- Summary Table ---
st.subheader("Daftar Prioritas Perbaikan (Belum Selesai & Error > 0%)")

df_display = (
    df[["tahapan", "wilayah", "status", "persentase"]]
    .sort_values("persentase", ascending=False)
    .reset_index(drop=True)
)
df_display.columns = ["Tahapan", "Wilayah", "Status", "Persentase (%)"]

st.dataframe(df_display, use_container_width=True, hide_index=True)

# --- Summary Bar: overall progress per tahapan ---
st.subheader("Ringkasan Progres Seluruh Tahapan")

summary_rows = []
for tahapan in TAHAPAN_ORDER:
    df_t = df[df["tahapan"] == tahapan]
    avg_persen = df_t["persentase"].mean() if not df_t.empty else 0
    count = len(df_t)
    summary_rows.append({"Tahapan": tahapan, "Rata-rata (%)": round(avg_persen, 2), "Jumlah Wilayah": count})

df_summary = pd.DataFrame(summary_rows)

fig_summary = go.Figure()
fig_summary.add_trace(
    go.Bar(
        x=df_summary["Tahapan"],
        y=df_summary["Rata-rata (%)"],
        text=df_summary["Rata-rata (%)"].astype(str) + "%",
        textposition="auto",
        marker_color="teal",
    )
)
fig_summary.update_layout(
    title="<b>Rata-rata Persentase Kendala per Tahapan</b>",
    xaxis_title="Tahapan Kegiatan",
    yaxis_title="Rata-rata (%)",
    yaxis=dict(range=[0, 105]),
    template="plotly_white",
)

st.plotly_chart(fig_summary, use_container_width=True)
st.dataframe(df_summary, use_container_width=True, hide_index=True)
