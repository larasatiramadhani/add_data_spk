import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time, timedelta
import time as tm
import threading
from datetime import date

st.set_page_config(page_title="Add SPK", layout="wide")

# URL dari Google Apps Script Web App
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbx3hzTtTqF2G7fyR7VdA0HtzIhYhDZr7tuGKPTlBYyoyozqnhho90Su02VIRqWjqG37/exec"

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


# Fungsi Ping Otomatis (Keep Alive)
# def keep_alive():
#     while True:
#         try:
#             response = requests.get(APPS_SCRIPT_URL, timeout=10)
#             print(f"Keep Alive Status: {response.status_code}")
#         except Exception as e:
#             print(f"Keep Alive Error: {e}")
#         tm.sleep(600)  # Ping setiap 10 menit

# # Menjalankan fungsi keep_alive di thread terpisah agar tidak mengganggu UI
# thread = threading.Thread(target=keep_alive, daemon=True)
# thread.start()

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
defaults = {
    "form_nomorSPK": generate_spk_number(), 
    "form_tanggal": date.today(), 
    "form_bu": "",
    "form_produk": "", 
    "form_line": "", 
    "form_start": datetime.now().time(), 
    "form_stop": datetime.now().time(), 
    "form_total_hour": "", 
    "form_speed": 0,
    "form_outputKG": "",
    "form_outputBatch": "",
    "form_innerRoll": "",
    "form_batch": 0,
    "form_roll": 0
}

# Pastikan semua nilai default ada di session state tanpa overwrite jika sudah ada
for key, value in defaults.items():
    st.session_state.setdefault(key, value)

# Pastikan form_add_reset ada di session_state
st.session_state.setdefault("form_add_reset", False)

# Reset nilai form jika form_add_reset bernilai True
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
    nomor_spk = st.text_input("Nomor SPK", value=st.session_state.get("form_nomorSPK"), key="form_nomorSPK", disabled=True)
with col2:
    tanggal = st.date_input("Tanggal", value=st.session_state.get("form_tanggal"), key="form_tanggal")

# Divider
st.markdown("---")

st.subheader("📦 Pilihan BU, Produk, Line")

# Pastikan kita hanya mengambil data yang valid
data_clean = [row for row in options.get("Dropdown List", []) if isinstance(row, list) and len(row) > 2]  # Pastikan ada minimal 3 kolom (BU, Line, Produk)

# Fungsi untuk mendapatkan daftar unik BU
def extract_unique_bu(data):
    try:
        return sorted(set(row[0] for row in data if row[0]))  # Pastikan nilai BU tidak kosong
    except Exception as e:
        st.error(f"Error saat mengekstrak BU: {e}")
        return []

# Fungsi untuk memfilter Produk dan Line berdasarkan BU yang dipilih
def filter_by_bu(data, selected_bu, column_index):
    try:
        return sorted(set(row[column_index] for row in data if row[0] == selected_bu and row[column_index]))
    except Exception as e:
        st.error(f"Error saat memfilter berdasarkan BU: {e}")
        return []

# Fungsi untuk memfilter Produk berdasarkan Line yang dipilih
def filter_by_line(data, selected_bu, selected_line, column_index):
    try:
        return sorted(set(row[column_index] for row in data if row[0] == selected_bu and row[1] == selected_line and row[column_index]))
    except Exception as e:
        st.error(f"Error saat memfilter berdasarkan Line: {e}")
        return []
def filter_by_line_forSpeed(data, selected_bu, selected_line, column_index):
    try:
        return sorted(set(row[column_index] for row in data if row[4] == selected_bu and row[5] == selected_line and row[column_index]))
    except Exception as e:
        st.error(f"Error saat memfilter berdasarkan Line: {e}")
        return []
def filter_by_speed(data, selected_bu, selected_line, selected_speed, column_index):
    try:
        return sorted(set(row[column_index] for row in data if row[4] == selected_bu and row[5] == selected_line and row[6]==selected_speed and row[column_index]))
    except Exception as e:
        st.error(f"Error saat memfilter berdasarkan Line: {e}")
        return []
def filter_by_batch(data, selected_bu, selected_line, selected_speed,selected_batch, column_index):
    try:
        return sorted(set(row[column_index] for row in data if row[4] == selected_bu and row[5] == selected_line and row[6]==selected_speed and row[7] == selected_batch and row[column_index]))
    except Exception as e:
        st.error(f"Error saat memfilter berdasarkan Line: {e}")
        return []
    
# Ambil daftar unik BU dari dataset
bu_options = extract_unique_bu(data_clean)  # Ambil BU dari options

if "form_bu" in st.session_state and st.session_state["form_bu"] not in bu_options:
    st.session_state["form_bu"] =  st.session_state.get("form_bu", "")

# Dropdown untuk BU
bu = st.selectbox("BU", [""] + bu_options, key="form_bu")

# Ambil daftar Line berdasarkan BU yang dipilih
list_line = filter_by_bu(data_clean, bu, 1) if bu else []

if "form_line" in st.session_state and st.session_state["form_line"] not in list_line:
    st.session_state["form_line"] =  st.session_state.get("form_line", "")

# Dropdown untuk Line
line = st.selectbox("Line", [""] + list_line, key="form_line")

# Ambil daftar Produk berdasarkan BU dan Line yang dipilih
list_produk = filter_by_line(data_clean, bu, line, 2) if bu and line else []

if "form_produk" in st.session_state and st.session_state["form_produk"] not in list_produk:
    st.session_state["form_produk"] = st.session_state.get("form_produk", "")

# Dropdown untuk Produk
produk = st.selectbox("Pilih Produk", [""] + list_produk, key="form_produk") 

if not bu or not line or not produk :
    st.error("⚠ Pilih BU, Line dan Produk terlebih dahulu")

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

if total_hour == timedelta(0):
        st.error("⚠ Pilih Jam Start dan Stop terlebih dahulu")

st.info(f"⏱ Total Durasi: {total_hour_time.strftime('%H:%M')} jam")

# Divider
st.markdown("---")

## SPEED ##
list_speed = filter_by_line_forSpeed(data_clean, bu, line, 6) if bu and line else []

col1, col2 = st.columns(2)
with col1:
    if st.session_state.form_line in list_speed:
        speed_index = list_speed.index(st.session_state.form_speed)
    else:
        speed_index = 0 
    speed = st.selectbox("Speed (kg/jam)",list_speed, index = speed_index, key="form_speed")
with col2:
    ## PILIH BATCH UNTUK MENGHITUNG OUTPUT BATCH ##
    list_batch = filter_by_speed(data_clean, bu, line,speed, 7) if bu and line else []
    if st.session_state.form_batch in list_batch:
        batch_index = list_batch.index(st.session_state.form_batch)
    else:
        batch_index = 0 
    batch = st.selectbox("Pilih Banyak Kg/Batch",list_batch, index = batch_index, key="form_batch")
## PILIH ROLL KG/ROLL UNTUK MENGHITUNG INNER ROLL ##
list_roll = filter_by_batch(data_clean, bu, line,speed,batch, 8) if bu and line else []
if st.session_state.form_roll in list_roll:
    roll_index = list_roll.index(st.session_state.form_roll)
else:
    roll_index = 0 
roll = st.selectbox("Pilih Banyak Kg/Roll",list_roll, index = roll_index, key="form_roll")

if not speed or not batch or not roll :
    st.error("⚠ Pilih Speed, Batch dan Roll terlebih dahulu")
# Divider
st.markdown("---")

try:
    speed = float(speed) if speed else 0.0
    batch = float(batch) if batch else 0.0
    roll = float(roll) if roll else 0.0
except ValueError:
    st.error("⚠ Gagal mengonversi nilai ke float. Pastikan input valid.")
    speed, batch, roll = 0.0, 0.0, 0.0

if speed != 0 and batch != 0 and roll != 0:
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

form_completed = all(st.session_state.get(key) for key in [
    "form_tanggal", "form_produk", "form_line", 
    "form_start", "form_stop", "form_speed", "form_batch", "form_roll"
])


submit_button = st.button("💾 Simpan Data", use_container_width=True,disabled=not form_completed)


# Jika tombol "Simpan Data" ditekan
if submit_button:
    try:
        formatted_tanggal = tanggal.strftime("%Y-%m-%d")  

        # Data yang akan dikirim ke Apps Script
        data = {
            "action": "add_data",
            "NomorSPK": nomor_spk,
            "Tanggal": formatted_tanggal,
            "BU": bu, 
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
        st.error(f"Error: {str(e)}")
