Kamu adalah seorang Senior Data Engineer dan Python Developer. Tugasmu adalah membangun sebuah aplikasi mini-ETL (Extract, Transform, Load) end-to-end untuk web scraping data monitoring, menggunakan Prefect sebagai orkestrator utamanya.

# Konteks Bisnis
Saya memiliki script manual berbasis Pandas dan Plotly yang sebelumnya membaca file Excel (berisi sheet: 'Pemutakhiran', 'Pencacahan', 'Pemeriksaan', 'Pengiriman ke KabKota', 'Penerimaan di KabKota', 'Penerimaan di IPDS', 'Pengolahan Dokumen K', 'Pengolahan Dokumen KP'). 
Sekarang, data tersebut berada di sebuah website. Saya ingin mengotomatisasi proses penarikan data tabel dari web, menyimpannya ke database, dan menampilkannya di dashboard.

# Spesifikasi Teknis & Stack
1. Orkestrasi: Prefect (versi 2.x atau 3.x). Gunakan dekorator @task dan @flow dengan implementasi retries, logging, dan error handling yang baik. (asumsikan saya sudah memiliki instance prefect yang sudah berjalan)
2. Ekstraksi (Scraping): Gunakan Playwright (mode headless) jika web membutuhkan rendering JavaScript, atau kombinasi httpx/requests + BeautifulSoup/Pandas jika HTML statis. Buat sistem yang deterministik (bukan LLM-based extraction).
3. Transformasi: Pandas.
4. Database (Load): SQLAlchemy dengan SQLite sebagai default awal (mudah dimigrasi ke PostgreSQL nantinya).
5. Visualisasi: Streamlit atau Dash (terintegrasi dengan Plotly untuk mempertahankan visualisasi bar chart dan data table dari script lama saya).

# Detail Logika Transformasi (Wajib Diikuti)
Di dalam Prefect @task untuk transformasi, terapkan logika yang sama dengan script lama saya:
- Lakukan otentikasi sso forticlient menggunakan package sso_auth yang sudah terinstall melalui pip
- Lakukan scraping pada url web berikut (contoh) :
https://webmonitoring.bps.go.id/sen/progress/pemutakhiran?wil=65&view=tabel&tgl_his=2026-02-26

https://webmonitoring.bps.go.id/sen/progress/pencacahan?wil=65&view=tabel&tgl_his=2026-02-26

https://webmonitoring.bps.go.id/sen/progress/edcod?wil=65&view=tabel&tgl_his=2026-02-26

https://webmonitoring.bps.go.id/sen/progress/pengiriman?wil=65&view=tabel&tgl_his=2026-02-26

https://webmonitoring.bps.go.id/sen/progress/penerimaan?wil=65&view=tabel&tgl_his=2026-02-26

https://webmonitoring.bps.go.id/sen/progress/ipds?wil=65&view=tabel&tgl_his=2026-02-26

https://webmonitoring.bps.go.id/sen/progress/pengolahan?wil=65&view=tabel&tgl_his=2026-02-26

https://webmonitoring.bps.go.id/sen/progress/pengolahan2?wil=65&view=tabel&tgl_his=2026-02-26

sesuaikan "tgl_his"
berikut contoh table nya
```html
<table class="table table-hover table-bordered tabel-rekap" id="tabel-progress">
            <thead>
                <tr>
                    <th class="" rowspan="2" style="text-align: center; vertical-align: middle;">Wilayah</th>
                    <th class="" rowspan="2" style="text-align: center; vertical-align: middle;">Target</th>
                    <th class="" colspan="2" style="text-align: center; vertical-align: middle;">Clean</th>
                    <th class="" colspan="2" style="text-align: center; vertical-align: middle;">Error</th>
                    
                </tr><tr>
                    <th class="col-data col-right" style="text-align: center; vertical-align: middle;">Jumlah</th>
                    <th class="col-data col-right" style="text-align: center; vertical-align: middle;">Persentase</th>
                    <th class="col-data col-right" style="text-align: center; vertical-align: middle;">Jumlah</th>
                    <th class="col-data col-right" style="text-align: center; vertical-align: middle;">Persentase</th>
                    
                </tr>
                <tr class="col-center nomor-kolom">
                    <td style="width: 15%; mso-number-format:'\@'; text-align:center; font-size: 80%;">(1)</td>
                    <td style="width: 7%; mso-number-format:'\@'; text-align:center; font-size: 80%;">(2)</td>
                    <td style="width: 7%; mso-number-format:'\@'; text-align:center; font-size: 80%;">(3)</td>
                    <td style="width: 7%; mso-number-format:'\@'; text-align:center; font-size: 80%;">(4)</td>
                    <td style="width: 8%; mso-number-format:'\@'; text-align:center; font-size: 80%;">(5)</td>
                    <td style="width: 8%; mso-number-format:'\@'; text-align:center; font-size: 80%;">(6)</td>
                   
                </tr>
            </thead>
            <tbody>
                                            <tr>
                    <td class="col-id" style="text-align: left;">
                                                    <a href="/sen/progress/pengolahan?wil=6501&amp;view=tabel&amp;tgl_his=2026-02-26">(6501) MALINAU</a>
                                            </td>
                                        
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-grey col-right">
                        550                    </td>
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        0                    </td>
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        0,00                    </td>

                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        84                    </td>
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        15,27                    </td>

                    

                </tr>
                                <tr>
                    <td class="col-id" style="text-align: left;">
                                                    <a href="/sen/progress/pengolahan?wil=6502&amp;view=tabel&amp;tgl_his=2026-02-26">(6502) BULUNGAN</a>
                                            </td>
                                        
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-grey col-right">
                        630                    </td>
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        0                    </td>
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        0,00                    </td>

                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        0                    </td>
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        0,00                    </td>

                    

                </tr>
                                <tr>
                    <td class="col-id" style="text-align: left;">
                                                    <a href="/sen/progress/pengolahan?wil=6503&amp;view=tabel&amp;tgl_his=2026-02-26">(6503) TANA TIDUNG</a>
                                            </td>
                                        
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-grey col-right">
                        510                    </td>
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        27                    </td>
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        5,29                    </td>

                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        123                    </td>
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        24,12                    </td>

                    

                </tr>
                                <tr>
                    <td class="col-id" style="text-align: left;">
                                                    <a href="/sen/progress/pengolahan?wil=6504&amp;view=tabel&amp;tgl_his=2026-02-26">(6504) NUNUKAN</a>
                                            </td>
                                        
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-grey col-right">
                        660                    </td>
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        115                    </td>
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        17,42                    </td>

                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        417                    </td>
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        63,18                    </td>

                    

                </tr>
                                <tr>
                    <td class="col-id" style="text-align: left;">
                                                    <a href="/sen/progress/pengolahan?wil=6571&amp;view=tabel&amp;tgl_his=2026-02-26">(6571) TARAKAN</a>
                                            </td>
                                        
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-grey col-right">
                        680                    </td>
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        0                    </td>
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        0,00                    </td>

                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        0                    </td>
                    <td style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        0,00                    </td>

                    

                </tr>
                                <tr>
                    <th style="mso-number-format:&quot;\@&quot;" class="col-id">Total</th>
                    <th style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        3.030                    </th>
                    <th style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        142                    </th>
                    <th style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        4,69                    </th>

                    <th style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        624                    </th>
                    <th style="mso-number-format:&quot;\@&quot;" class="col-data col-right">
                        20,59                    </th>

                    
                </tr>
            </tbody>
        </table>
```

- Ambil data tabel hasil scraping.
- Filter baris pada kolom pertama (Wilayah) yang hanya mengandung teks "(65".
- Bersihkan kolom Wilayah dengan menghapus kode dalam kurung menggunakan regex (contoh: `r'\(.*\) '`).
- Tentukan `label_status`: Jika nama tahapan mengandung kata "Pengolahan", statusnya "Error". Jika tidak, statusnya "Belum Selesai".
- Konversi nilai persentase di kolom indeks ke-5 (kolom ke-6) menjadi numerik (`pd.to_numeric`).
- Hanya simpan baris yang nilai persentasenya > 0.
- Tambahkan timestamp `scraped_at` untuk tracking histori data.

# Struktur Proyek yang Diharapkan
Berikan output berupa struktur direktori dan kode lengkap untuk file-file berikut:
1. `requirements.txt`: Daftar dependencies.
2. `src/database.py`: Setup SQLAlchemy engine, declarative base, dan skema tabel (kolom: id, tahapan, wilayah, status, persentase, scraped_at). Buat fungsi upsert/insert.
3. `src/scraper.py`: Fungsi scraping untuk mengambil HTML/tabel berdasarkan URL.
4. `src/etl_flow.py`: File utama Prefect berisi @task (extract, transform, load) dan @flow. Terapkan `retries=3` dan `retry_delay_seconds=10` pada task scraping.
5. `app.py`: Aplikasi Streamlit/Dash untuk membaca data dari database SQLite dan merender visualisasi Plotly (subplot 4x2) serta tabel ringkasan seperti script awal saya.

# Instruksi Tambahan untuk Output
- Tuliskan kode dengan type hinting (`-> dict`, `-> pd.DataFrame`, dll) dan docstrings.
- Gunakan `get_run_logger()` dari Prefect untuk mencatat setiap langkah (misal: jumlah baris yang berhasil diekstrak, error per tahapan).
- Berikan instruksi Markdown di akhir tentang cara:
  1. Menjalankan migrasi database awal.
  2. Menjalankan flow Prefect secara lokal.
  3. Mendaftarkan deployment Prefect (schedule harian).
  4. Menjalankan dashboard Streamlit/Dash.

Tanyakan kepada saya 2 hal berikut sebelum mulai menulis kode penuh:
1. Apa daftar lengkap URL web target untuk masing-masing tahapan?
2. Apakah halaman web tersebut memerlukan proses login (memasukkan username/password) sebelum tabelnya bisa diakses? tidak perlu