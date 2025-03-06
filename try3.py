import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time, timedelta
import time as tm
import requests
import locale
from datetime import date
st.set_page_config(page_title="Login", page_icon="🔐", layout="wide")
# URL dari Google Apps Script Web App
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzpjfcCG6PjXDhMAxKqRkYY5hg9CjazA_uCaenC_6-Q-99LDF0NTR7mukBf8tQNg40KoQ/exec"

# Fungsi untuk mendapatkan semua data dari Google Sheets
def get_all_data():
    try:
        response = requests.get(APPS_SCRIPT_URL, params={"action": "get_data"}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Terjadi kesalahan saat mengambil data: {e}")
        return []

# Fungsi untuk mendapatkan opsi dari Google Sheets
def get_options():
    try:
        response = requests.get(APPS_SCRIPT_URL, params={"action": "get_options"}, timeout=10)
        response.raise_for_status()
        options = response.json()
        for key in options:
            options[key].insert(0, "")  # Tambahkan opsi kosong sebagai default
        return options
    except requests.exceptions.RequestException as e:
        st.error(f"Terjadi kesalahan saat mengambil data: {e}")
        return {}

# Fungsi untuk mengirim data ke Google Sheets
def add_data(form_data):
    try:
        response = requests.post(APPS_SCRIPT_URL, json=form_data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "error": str(e)}

# Fungsi untuk menghapus data
def delete_data(unique_key):
    try:
        response = requests.post(APPS_SCRIPT_URL, json={"action": "delete", "unique_key": unique_key}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "error": str(e)}

# Fungsi untuk memperbarui data
def update_data(updated_row):
    try:
        response = requests.post(APPS_SCRIPT_URL, json={"action": "update", "updated_row": updated_row}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "error": str(e)}

bulan_romawi = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
    7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"
}
# Fungsi untuk mendapatkan nomor SPK otomatis
def generate_spk_number():
    all_data = get_all_data()
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_month_romawi = bulan_romawi[current_month]  # Konversi bulan ke Romawi

    # Ambil semua nomor SPK untuk bulan dan tahun ini
    spk_numbers = [
        row[0] for row in all_data
        if len(row) > 0 and f"/{current_month_romawi}/{current_year}" in row[0]
    ]

    if spk_numbers:
        # Ambil nomor terakhir dan tambahkan 1
        last_spk = max(spk_numbers)  # Ambil nomor terbesar
        last_number = int(last_spk.split("/")[0])  # Ambil angka sebelum "/PR/"
        new_number = last_number + 1
    else:
        # Jika belum ada SPK bulan ini, mulai dari 1
        new_number = 1

    # Format nomor SPK baru
    return f"{str(new_number).zfill(2)}/PR/{current_month_romawi}/{current_year}"

# Ambil data dari Google Sheets
all_data = get_all_data()

# Ambil data untuk select box
options = get_options()
defaults = {"form_nomorSPK": generate_spk_number(), 
            "form_tanggal": date.today(), 
            "form_produk": "", 
            "form_line": "", 
            "form_start": datetime.now().time(), 
            "form_stop": datetime.now().time(), 
            "form_total_hour": "", 
            "form_speed": 280.67,
            "form_outputKG":"",
            "form_outputBatch":"",
            "form_innerRoll":"",
            "form_batch": 1000,
            "form_roll" : 75.9
            }

# Pastikan semua nilai default ada di session state tanpa overwrite jika sudah ada
for key, value in defaults.items():
    st.session_state.setdefault(key, value)

# Pastikan form_add_reset ada di session_state
st.session_state.setdefault("form_add_reset", False)

# Reset nilai form jika `form_add_reset` bernilai True
if st.session_state.form_add_reset:
    st.session_state.update(defaults)
    st.session_state.form_add_reset = False  # Kembalikan ke False setelah reset

st.title("📄 Surat Perintah Kerja")  

# Divider
st.markdown("---")

## NO SPK & TANGGAL ##
st.subheader("📌 Informasi SPK")  
col1, col2 = st.columns(2)  
with col1:
    nomor_spk = st.text_input("Nomor SPK", value=st.session_state.get("form_nomorSPK"), key="form_nomorSPK")
with col2:
    tanggal = st.date_input("Tanggal", value=st.session_state.get("form_tanggal"), key="form_tanggal")

# Divider
st.markdown("---")

## PRODUK & LINE ##
st.subheader("📦 Pilihan Produk & Line")  
col1, col2 = st.columns(2)  
with col1:
    list_produk = [item[0] if isinstance(item, list) and item else item for item in options.get("List Produk", [""])]
    if st.session_state.form_produk in list_produk:
        produk_index = list_produk.index(st.session_state.form_produk)
    else:
        produk_index = ""  # Gunakan indeks "" jika nilai default tidak ditemukan
    produk = st.selectbox("Pilih Produk", list_produk, index = produk_index, key="form_produk")
with col2:
    ## LINE ##
    list_line = [item[0] if isinstance(item, list) and item else item for item in options.get("List Line", [""])]
    if st.session_state.form_line in list_line:
        line_index = list_line.index(st.session_state.form_line)
    else:
        line_index = ""  # Gunakan indeks "" jika nilai default tidak ditemukan
    line = st.selectbox("Line", list_line, index = line_index, key="form_line")

# Divider
st.markdown("---")

## START & STOP ##
st.subheader("⏳ Waktu Produksi")  
col1, col2 = st.columns(2)
with col1:
    start_time = st.time_input("Jam Start", value=st.session_state.get("form_start"), key="form_start")
with col2:
    stop_time = st.time_input("Jam Stop", value=st.session_state.get("form_stop"), key="form_stop")

## TOTAL HOUR ##
start_datetime = datetime.combine(date.today(), start_time)
stop_datetime = datetime.combine(date.today(), stop_time)

if stop_datetime < start_datetime:
    stop_datetime += timedelta(days=1)
total_hour = stop_datetime - start_datetime
base_time = datetime(1900, 1, 1)
total_hour_time = (base_time + total_hour).time()

st.info(f"⏱️ Total Durasi: {total_hour_time.strftime('%H:%M')} jam")

# Divider
st.markdown("---")

## SPEED ##
col1, col2 = st.columns(2)
with col1:
    list_speed = [280.67, 780.00]
    if st.session_state.form_line in list_speed:
        speed_index = list_speed.index(st.session_state.form_speed)
    else:
        speed_index = 0 # Gunakan indeks "" jika nilai default tidak ditemukan
    speed = st.selectbox("Speed (kg/jam)",list_speed, index = speed_index, key="form_speed")

with col2:
    ## PILIH BATCH UNTUK MENGHITUNG OUTPUT BATCH ##
    list_batch = [1000.00, 130.00]
    if st.session_state.form_batch in list_batch:
        batch_index = list_batch.index(st.session_state.form_batch)
    else:
        batch_index = 0 # Gunakan indeks "" jika nilai default tidak ditemukan
    batch = st.selectbox("Pilih Banyak Kg/Batch",list_batch, index = batch_index, key="form_batch")

## PILIH ROLL KG/ROLL UNTUK MENGHITUNG INNER ROLL ##
list_roll = [75.9, 75.0]
if st.session_state.form_roll in list_roll:
    roll_index = list_roll.index(st.session_state.form_roll)
else:
    roll_index = 0 # Gunakan indeks "" jika nilai default tidak ditemukan
roll = st.selectbox("Pilih Banyak Kg/Roll",list_roll, index = roll_index, key="form_roll")

# Divider
st.markdown("---")

##  MENGHITUNG OUTPUT KG ##
total_hour_float = total_hour.total_seconds() / 3600
OutputKG = total_hour_float * speed

## MENGHITUNG OUTPUT BATCH ##
OutputBatch = round(OutputKG / batch,1)
InnerRoll = round(OutputKG / roll,0)

## MENAMPILKAN  OUTPUTKG, OUTPUT BATCH DI UI ##
st.subheader("📊 Hasil Perhitungan")  
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Output (kg)", f"{OutputKG:.2f} kg")
with col2:
    st.metric("Total Output (Batch)", f"{OutputBatch:.1f} batch")
with col3:
    st.metric("Total Inner (Roll)", f"{InnerRoll:.1f} roll")

# Tombol Simpan
st.markdown("---")
submit_button = st.button("💾 Simpan Data", use_container_width=True)


# Jika tombol "Simpan Data" ditekan
if submit_button:
    try:
        # Atur locale ke Bahasa Indonesia untuk format tanggal
        # Mapping nama hari dan bulan
        nama_hari = {
            "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
            "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
        }

        nama_bulan = {
            "January": "Januari", "February": "Februari", "March": "Maret",
            "April": "April", "May": "Mei", "June": "Juni", "July": "Juli",
            "August": "Agustus", "September": "September", "October": "Oktober",
            "November": "November", "December": "Desember"
        }

        # Ambil tanggal saat ini
        tanggal = datetime.now()

        # Format default (Inggris)
        hari_eng = tanggal.strftime("%A")
        bulan_eng = tanggal.strftime("%B")

        # Ganti dengan bahasa Indonesia
        hari_id = nama_hari[hari_eng]
        bulan_id = nama_bulan[bulan_eng]
        formatted_tanggal = f"{hari_id}, {tanggal.day} {bulan_id} {tanggal.year}"  

        # Data yang akan dikirim ke Apps Script
        data = {
            "action": "add_data",
            "NomorSPK": nomor_spk,
            "Tanggal": formatted_tanggal,
            "Produk": produk,
            "Line": line,
            "Speed": speed,
            "Start": start_time.strftime("%H:%M"),
            "Stop": stop_time.strftime("%H:%M"),
            "TotalHour" : total_hour_time.strftime("%H:%M"),
            "OutputKG" : OutputKG,
            "OutputBatch" : OutputBatch,
            "InnerRoll" : InnerRoll
        }

        # Kirim data ke Apps Script menggunakan POST request
        response = requests.post(APPS_SCRIPT_URL, json=data)
        result = response.json()

        if result.get("status") == "success":
            st.success("Data berhasil ditambahkan!")
            st.session_state.form_add_reset = True
            st.rerun() 

        else:
            st.error(f"Terjadi kesalahan: {result.get('error')}")

    except Exception as e:
        st.error(f"Error: {str(e)}")
