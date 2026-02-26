```python
import pandas as pd
import plotly.express as px

file_path = "Monitoring SUSENAS 23_02.xlsx"
xls = pd.ExcelFile(file_path)

summary = []

def clean_sheet(sheet):
    df = pd.read_excel(xls, sheet_name=sheet)
    df = df.iloc[2:].reset_index(drop=True)

    df = df[~df.iloc[:,0].astype(str).str.contains("Total", case=False, na=False)]

    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.fillna(0)

    total_target = df.iloc[:,1].sum()
    total_selesai = df.iloc[:,2].sum()

    persen = (total_selesai / total_target) * 100 if total_target > 0 else 0

    return total_target, total_selesai, persen

for sheet in xls.sheet_names:
    target, selesai, persen = clean_sheet(sheet)
    summary.append([sheet, target, selesai, persen])

summary_df = pd.DataFrame(summary, columns=["Tahap", "Target", "Selesai", "Persentase"])

summary_df
```

```python
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

file_path = 'Monitoring SUSENAS 23_02.xlsx'

sheets = ['Pemutakhiran', 'Pencacahan', 'Pemeriksaan', 'Pengiriman ke KabKota', 'Penerimaan di KabKota', 'Penerimaan di IPDS', 'Pengolahan Dokumen K', 'Pengolahan Dokumen KP']

summary_data = []

try:
    for s in sheets:

        df_temp = pd.read_excel(file_path, sheet_name=s)
        total_pct = df_temp[df_temp.iloc[:, 0] == 'Total'].iloc[0, 3]
        summary_data.append({'Tahapan': s.capitalize(), 'Progres (%)': total_pct})

    df_summary = pd.DataFrame(summary_data)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_summary['Tahapan'],
        y=df_summary['Progres (%)'],
        text=df_summary['Progres (%)'].astype(str) + '%',
        textposition='auto',
        marker_color='teal'
    ))

    fig.update_layout(
        title='<b>Monitoring Progres Seluruh Tahapan SUSENAS</b>',
        xaxis_title='Tahapan Kegiatan',
        yaxis_title='Persentase Selesai (%)',
        yaxis=dict(range=[0, 105]),
        template='plotly_white'
    )

    fig.show()

except Exception as e:
    print(f"❌ Error: Pastikan nama sheet di file Excel sama dengan daftar di kode. Error detail: {e}")
```

```python
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

file_path = 'Monitoring SUSENAS 23_02.xlsx'
list_sheets = [
    'Pemutakhiran', 'Pencacahan', 'Pemeriksaan', 'Pengiriman ke KabKota',
    'Penerimaan di KabKota', 'Penerimaan di IPDS', 'Pengolahan Dokumen K', 'Pengolahan Dokumen KP'
]

fig = make_subplots(
    rows=4, cols=2,
    subplot_titles=list_sheets,
    vertical_spacing=0.08,
    horizontal_spacing=0.1
)

for i, sheet in enumerate(list_sheets):
    try:

        df = pd.read_excel(file_path, sheet_name=sheet)
        df_filtered = df[df.iloc[:, 0].str.contains(r'\(65', na=False)].copy()

        wilayah = df_filtered.iloc[:, 0].str.replace(r'\(.*\) ', '', regex=True)
        persen = pd.to_numeric(df_filtered.iloc[:, 3], errors='coerce').fillna(0)

        row = (i // 2) + 1
        col = (i % 2) + 1

        fig.add_trace(
            go.Bar(
                x=wilayah,
                y=persen,
                name=sheet,
                text=persen.astype(str) + '%',
                textposition='auto',
                # Warna dinamis: Hijau jika 100%, Biru jika proses, Merah jika 0%
                marker_color=['#2ecc71' if p == 100 else '#3498db' if p > 0 else '#e74c3c' for p in persen]
            ),
            row=row, col=col
        )

        fig.update_yaxes(range=[0, 115], row=row, col=col)

    except Exception as e:
        print(f"⚠️ Sheet '{sheet}' bermasalah atau tidak ditemukan. Error: {e}")

fig.update_layout(
    height=1400,
    width=1100,
    title_text="<b>DASHBOARD MONITORING SUSENAS KALIMANTAN UTARA 2026</b><br><sup>Menampilkan Persentase Selesai dan Tingkat Clean per Tahapan</sup>",
    title_x=0.5,
    showlegend=False,
    template='plotly_white'
)

fig.show()
```

```python
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

file_path = 'Monitoring SUSENAS 23_02.xlsx'
list_sheets = [
    'Pemutakhiran', 'Pencacahan', 'Pemeriksaan', 'Pengiriman ke KabKota',
    'Penerimaan di KabKota', 'Penerimaan di IPDS', 'Pengolahan Dokumen K', 'Pengolahan Dokumen KP'
]

summary_list = []

fig = make_subplots(
    rows=4, cols=2,
    subplot_titles=list_sheets,
    vertical_spacing=0.1,
    horizontal_spacing=0.1
)

for i, sheet in enumerate(list_sheets):
    try:
        df = pd.read_excel(file_path, sheet_name=sheet)
        df_filtered = df[df.iloc[:, 0].str.contains(r'\(65', na=False)].copy()

        wilayah = df_filtered.iloc[:, 0].str.replace(r'\(.*\) ', '', regex=True)


        if 'Pengolahan' in sheet:
            label_status = "Error"
            kolom_idx = 5
        else:
            label_status = "Belum Selesai"
            kolom_idx = 5

        nilai = pd.to_numeric(df_filtered.iloc[:, kolom_idx], errors='coerce').fillna(0)

        for w, v in zip(wilayah, nilai):
            if v > 0:
                summary_list.append({'Tahapan': sheet, 'Wilayah': w, 'Status': label_status, 'Persentase (%)': v})

        row = (i // 2) + 1
        col = (i % 2) + 1

        # Warna: Merah jika > 0 (artinya ada yg belum selesai/error), Hijau jika 0
        colors = ['#e74c3c' if val > 0 else '#2ecc71' for val in nilai]

        fig.add_trace(
            go.Bar(
                x=wilayah,
                y=nilai,
                name=label_status,
                text=nilai.astype(str) + '%',
                textposition='auto',
                marker_color=colors,
                hovertemplate=f"Wilayah: %{{x}}<br>{label_status}: %{{y}}%<extra></extra>"
            ),
            row=row, col=col
        )

        fig.layout.annotations[i].update(text=f"<b>{sheet}</b><br>({label_status})")
        fig.update_yaxes(title_text="%", range=[0, 115], row=row, col=col)

    except Exception as e:
        print(f"⚠️ Error pada sheet '{sheet}': {e}")

fig.update_layout(
    height=1300, width=1000,
    title_text="<b>DASHBOARD MONITORING KENDALA SUSENAS (BELUM SELESAI & ERROR)</b>",
    title_x=0.5,
    showlegend=False,
    template='plotly_white'
)


fig.show()

print("\n" + "!"*60)
print("  DAFTAR PRIORITAS PERBAIKAN (BELUM SELESAI & ERROR > 0%)")
print("!"*60)

if summary_list:
    df_summary = pd.DataFrame(summary_list).sort_values(by='Persentase (%)', ascending=False)
    from google.colab import data_table
    display(data_table.DataTable(df_summary, include_index=False, num_rows_per_page=10))
else:
    print("✅ Luar biasa! Semua tahapan sudah 100% Selesai dan 0% Error.")
```

```python
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

file_path = 'Monitoring SUSENAS 23_02.xlsx'

list_sheets = [
    'Pemutakhiran', 'Pencacahan', 'Pemeriksaan', 'Pengiriman ke KabKota',
    'Penerimaan di KabKota', 'Penerimaan di IPDS', 'Pengolahan Dokumen K', 'Pengolahan Dokumen KP'
]

fig = make_subplots(
    rows=4, cols=2,
    subplot_titles=[f"Sisa/Error: {s}" for s in list_sheets],
    vertical_spacing=0.08,
    horizontal_spacing=0.1
)

for i, sheet in enumerate(list_sheets):
    try:
        df = pd.read_excel(file_path, sheet_name=sheet)

        df_filtered = df[df.iloc[:, 0].str.contains(r'\(65', na=False)].copy()
        wilayah = df_filtered.iloc[:, 0].str.replace(r'\(.*\) ', '', regex=True)

        nilai_negatif = pd.to_numeric(df_filtered.iloc[:, 5], errors='coerce').fillna(0)

        row = (i // 2) + 1
        col = (i % 2) + 1

        colors = ['#e74c3c' if val > 50 else '#f1c40f' if val > 0 else '#2ecc71' for val in nilai_negatif]

        fig.add_trace(
            go.Bar(
                x=wilayah,
                y=nilai_negatif,
                name=sheet,
                text=nilai_negatif.astype(str) + '%',
                textposition='auto',
                marker_color=colors
            ),
            row=row, col=col
        )

        y_label = "Error (%)" if "Pengolahan" in sheet else "Belum Selesai (%)"
        fig.update_yaxes(title_text=y_label, range=[0, 115], row=row, col=col, title_font=dict(size=10))

    except Exception as e:
        print(f"⚠️ Sheet '{sheet}' bermasalah. Error: {e}")

fig.update_layout(
    height=1400,
    width=1100,
    title_text="<b>DASHBOARD MONITORING KEKURANGAN & ERROR SUSENAS</b><br><sup>Menampilkan Persentase Belum Selesai dan Tingkat Error per Tahapan</sup>",
    title_x=0.5,
    showlegend=False,
    template='plotly_white'
)

fig.show()
```