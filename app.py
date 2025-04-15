import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Crypto Risk Analyzer", layout="wide")
st.title("✅ Final Format Tabel Tanpa Position Size")

# Inisialisasi state
if "data" not in st.session_state:
    st.session_state.data = []

with st.form("signal_input_form"):
    st.subheader("📥 Masukkan Sinyal Trading")
    raw_signal = st.text_area("Paste sinyal di sini:", height=200)
    entry_exec = st.number_input("Entry Eksekusi (Entry E)", format="%.8f")
    max_tp_hit = st.selectbox("Max TP Hit (yang benar-benar tercapai)", ["TP1", "TP2", "TP3", "TP4"])
    close_at = st.selectbox("Close At (kapan kamu keluar)", ["TP1", "TP2", "TP3", "TP4", "SL", "Custom"])
    custom_close = st.number_input("Jika 'Close At' = Custom, masukkan harga close:", format="%.8f")
    submitted = st.form_submit_button("📊 Tambahkan ke Tabel")

if submitted and raw_signal and entry_exec:
    # Parsing dari teks
    try:
        pair = re.search(r"([A-Z]+USDT)", raw_signal).group(1)
        entry_signal = float(re.search(r"Entry:\s*([\d.]+)", raw_signal).group(1))
        sl = float(re.search(r"Stop loss 1:\s*([\d.]+)", raw_signal).group(1))
        tp1 = float(re.search(r"Target 1:\s*([\d.]+)", raw_signal).group(1))
        tp2 = float(re.search(r"Target 2:\s*([\d.]+)", raw_signal).group(1))
        tp3 = float(re.search(r"Target 3:\s*([\d.]+)", raw_signal).group(1))
        tp4 = float(re.search(r"Target 4:\s*([\d.]+)", raw_signal).group(1))

        def gain_pct(tp):
            return (tp - entry_exec) / entry_exec * 100

        def rrr(tp):
            return round((tp - entry_exec) / (entry_exec - sl), 2)

        sl_pct = (entry_exec - sl) / entry_exec * 100

        # Tentukan harga close
        close_map = {"TP1": tp1, "TP2": tp2, "TP3": tp3, "TP4": tp4, "SL": sl, "Custom": custom_close}
        close_price = close_map[close_at]
        realized_pct = (close_price - entry_exec) / entry_exec * 100

        # Tambahkan ke data
        st.session_state.data.append({
            "Pair": pair,
            "Entry E": entry_exec,
            "SL (Loss %)": f"{sl:.4f} ({-sl_pct:.2f}%)",
            "TP1 (Gain %, RRR)": f"{tp1:.4f} (+{gain_pct(tp1):.2f}%, {rrr(tp1)})",
            "TP2 (Gain %, RRR)": f"{tp2:.4f} (+{gain_pct(tp2):.2f}%, {rrr(tp2)})",
            "TP3 (Gain %, RRR)": f"{tp3:.4f} (+{gain_pct(tp3):.2f}%, {rrr(tp3)})",
            "TP4 (Gain %, RRR)": f"{tp4:.4f} (+{gain_pct(tp4):.2f}%, {rrr(tp4)})",
            "Max TP Hit": max_tp_hit,
            "Close At": close_at,
            "Realized Gain %": f"{realized_pct:+.2f}%"
        })
    except Exception as e:
        st.error(f"Gagal parsing sinyal. Pastikan format sinyal benar. Error: {e}")

# Tampilkan tabel jika ada data
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
    st.dataframe(df, use_container_width=True)

    with st.expander("🔽 Unduh Data"):
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("💾 Download CSV", data=csv, file_name="signal_log.csv", mime="text/csv")
