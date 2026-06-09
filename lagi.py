import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error
import plotly.graph_objects as go
from datetime import datetime
from zoneinfo import ZoneInfo

st.write(datetime.now(ZoneInfo("Asia/Jakarta")))
    
# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Prediksi Cuaca BMKG",
    page_icon="🌦️",
    layout="wide"
)

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🌦️ Menu")

menu = st.sidebar.radio(
    "Pilih Menu",
    ["🏠 Dashboard", "📊 Dataset", "🔮 Prediksi", "📈 Evaluasi"]
)

kota_dict = {
    "Surabaya": "35.78.01.1001",
    "Jakarta": "31.71.01.1001",
    "Bandung": "32.73.01.1001",
    "Semarang": "33.74.01.1001",
    "Yogyakarta": "34.71.01.1001"
}

kota = st.sidebar.selectbox("📍 Kota", list(kota_dict.keys()))

# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=600)
def load_data(adm4):
    url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={adm4}"
    r = requests.get(url)
    js = r.json()

    rows = []
    for hari in js["data"][0]["cuaca"]:
        for item in hari:
            dt = datetime.strptime(item["local_datetime"], "%Y-%m-%d %H:%M:%S")

            rows.append({
                "datetime": dt,
                "tanggal": dt.date(),
                "jam": dt.hour,
                "suhu": float(item["t"]),
                "kelembapan": float(item["hu"]),
                "angin": float(item["ws"]),
                "cuaca": item["weather_desc"]
            })

    return pd.DataFrame(rows)

df = load_data(kota_dict[kota])
latest = df.iloc[-1]

# =========================
# MODEL
# =========================
X = df[["jam", "kelembapan", "angin"]]
y = df["suhu"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

rf_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)
rf_model.fit(X_train, y_train)

xgb_model = XGBRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=4,
    random_state=42
)
xgb_model.fit(X_train, y_train)

rf_pred_test = rf_model.predict(X_test)
xgb_pred_test = xgb_model.predict(X_test)

rf_mape = mean_absolute_percentage_error(y_test, rf_pred_test) * 100
xgb_mape = mean_absolute_percentage_error(y_test, xgb_pred_test) * 100

# =========================
# DYNAMIC COLOR LOGIC (REALTIME TIME-BASED)
# =========================
jam_sekarang = datetime.now().hour

if 6 <= jam_sekarang < 18:
    # SIANG: Background cerah, teks utama & teks sidebar otomatis GELAP
    bg_gradient = "linear-gradient(180deg, #bae6fd, #e0f2fe)"
    text_color = "#0f172a" 
    sidebar_text_color = "#0f172a"
    card_bg = "rgba(15, 23, 42, 0.06)" 
    card_border = "rgba(15, 23, 42, 0.12)"
    grid_color = "rgba(0, 0, 0, 0.1)"
    cloud_color = "rgba(255, 255, 255, 0.75)"  
else:
    # MALAM: Background gelap, teks utama & teks sidebar otomatis TERANG
    bg_gradient = "linear-gradient(180deg, #0f172a, #1e293b)"
    text_color = "#ffffff"
    sidebar_text_color = "#ffffff"
    card_bg = "rgba(255, 255, 255, 0.08)" 
    card_border = "rgba(255, 255, 255, 0.15)"
    grid_color = "rgba(255, 255, 255, 0.1)"
    cloud_color = "rgba(255, 255, 255, 0.25)"  

# =========================
# STYLE FIX FULL
# =========================
st.markdown(f"""
<style>

/* BACKGROUND UTAMA */
.stApp {{
    background: {bg_gradient};
}}

/* CUSTOM TEXT CONTRAST CLASS */
.main-text {{
    color: {text_color} !important;
}}

/* FIX LABEL DI ATAS INPUT - MENYATU TRANSPARAN */
div[data-testid="stWidgetLabel"] label, 
div[data-testid="stWidgetLabel"] p,
div[data-testid="stWidgetLabel"] span,
.stSlider label,
.stSlider div {{
    color: {text_color} !important;
    background: transparent !important;
    background-color: transparent !important;
    font-weight: 600 !important;
    opacity: 0.9 !important;
    box-shadow: none !important;
    text-shadow: none !important;
    padding: 0 !important;
}}

/* FIX METRIC VALUE */
div[data-testid="stMetricValue"] {{
    color: {text_color} !important;
}}
div[data-testid="stMetricLabel"] p {{
    color: {text_color} !important;
    opacity: 0.7;
}}

/* ========================================================
   FIX SKALA JAM SLIDER MERAH MINIMALIS MODERN
   ======================================================== */
div[data-testid="stSlider"] div,
div[data-testid="stSlider"] span,
div[data-testid="stSlider"] p {{
    background-color: transparent !important;
    background: transparent !important;
    box-shadow: none !important;
}}

div[data-testid="stSlider"] div[role="slider"] {{
    background-color: #ef4444 !important;
    border: none !important;
}}

div[data-testid="stSlider"] div[data-baseweb="slider"] div div {{
    background: #ef4444 !important;
}}

div[data-testid="stSlider"] div[data-baseweb="slider"] div[role="slider"] div {{
    color: #ef4444 !important;
    font-weight: 700 !important;
}}

div[data-testid="stSlider"] div[data-baseweb="slider"] + div div {{
    color: #ef4444 !important;
    font-weight: 600 !important;
}}

# ========================================================
# REVISI TOTAL
# ======================================================== */
/* Box Utama Input */
div[data-baseweb="input"], 
div[data-baseweb="select"],
div[data-baseweb="select"] > div,
div[data-baseweb="popover"] div, 
div[data-baseweb="popover"] input {{
    border: none !important;
    outline: none !important;
    border-radius: 10px !important;
    background-color: #f8fafc !important; /* Warna basis putih solid bersih */
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05) !important;
    transition: background-color 0.2s ease !important;
}}

/* Menghapus garis pemisah */
div[data-baseweb="input"] div, 
div[data-baseweb="input"] button {{
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}}

/* Focus State */
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="input"]:focus-within,
input:focus, 
div[role="combobox"]:focus-within {{
    border: none !important;
    background-color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    outline: none !important;
}}

/* Mengunci Teks di Dalam Input Box */
div[data-baseweb="select"] div,
div[data-baseweb="select"] span,
div[data-baseweb="input"] input,
.stSelectbox div[role="button"] {{
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    font-weight: 500 !important;
}}

/* ========================================================
   DROPDOWN LISTBOX
   ======================================================== */
div[role="listbox"] {{
    background-color: #ffffff !important;
    border-radius: 10px !important;
    border: none !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
    padding: 5px !important;
}}

/* Membersihkan baris item di dalam listbox*/
div[role="listbox"] li,
div[role="listbox"] li div,
div[role="listbox"] li span {{
    border: none !important;
    box-shadow: none !important;
    background-color: transparent !important;
    color: #334155 !important;
}}

/* Efek hover item */
div[role="listbox"] li:hover,
div[role="listbox"] li[aria-selected="true"] {{
    background-color: #f1f5f9 !important;
    border-radius: 6px !important;
}}

/* ========================================================
   MODERN KALENDER (st.date_input)
   ======================================================== */
div[data-baseweb="calendar"] {{
    background-color: #ffffff !important;
    border-radius: 12px !important;
    border: none !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
    padding: 12px !important;
}}
div[data-baseweb="calendar"] *, 
div[data-baseweb="calendar"] div,
div[data-baseweb="calendar"] button {{
    color: #1e293b !important;
    border: none !important;
    box-shadow: none !important;
    background-color: transparent !important;
}}
div[data-baseweb="calendar"] div[role="gridcell"] button {{
    border-radius: 50% !important;
}}
div[data-baseweb="calendar"] div[aria-selected="true"] button {{
    background-color: #ef4444 !important;
    color: #ffffff !important;
}}

/* FIX KOTAK*/
div[data-testid="stNotification"],
.stAlert, 
div.element-container div[role="alert"] {{
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-left: 4px solid #22c55e !important; /* Aksen garis hijau minimalis di kiri */
    border-radius: 10px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
}}
div[data-testid="stNotification"] *,
.stAlert *,
div.element-container div[role="alert"] * {{
    color: #15803d !important;
    -webkit-text-fill-color: #15803d !important;
    font-weight: 600 !important;
}}

/* SIDEBAR - SELALU CLEARGLASS */
section[data-testid="stSidebar"] {{
    background: rgba(255, 255, 255, 0.15) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.2) !important;
}}
section[data-testid="stSidebar"] *, 
section[data-testid="stSidebar"] label, 
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] p {{
    color: {sidebar_text_color};
}}
section[data-testid="stSidebar"] div[data-baseweb="select"] div,
section[data-testid="stSidebar"] div[data-baseweb="select"] span {{
    color: #000000 !important;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label {{
    font-weight: 600;
    font-size: 16px;
    padding: 6px 10px;
    border-radius: 8px;
    transition: all 0.2s ease-in-out;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] div[aria-checked="true"] {{
    background: linear-gradient(90deg, rgba(59, 130, 246, 0.8), rgba(6, 182, 212, 0.8)) !important;
    border-radius: 10px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
}}
section[data-testid="stSidebar"] div[role="radiogroup"] div[aria-checked="true"] label span {{
    color: #ffffff !important;
    font-weight: 700;
}}

.stButton > button {{
    background: linear-gradient(90deg, #3b82f6, #06b6d4);
    color: white !important;
    border-radius: 10px;
    font-weight: bold;
    border: none;
}}

.card {{
    background: {card_bg};
    backdrop-filter: blur(10px);
    border: 1px solid {card_border};
    padding: 18px;
    border-radius: 15px;
    text-align: center;
    color: {text_color};
}}

.city-title {{
    color: {text_color} !important;
    font-size: 18px;
    font-weight: 600;
}}

/* AWAN*/
.cloud {{
    position: fixed;
    background: {cloud_color};
    border-radius: 50px;
    z-index: 0;
    animation: move 35s linear infinite;
    filter: blur(2px);
}}
.cloud::before {{
    content: '';
    position: absolute;
    background: {cloud_color};
    width: 60px;
    height: 60px;
    top: -30px;
    left: 20px;
    border-radius: 50%;
}}
.cloud::after {{
    content: '';
    position: absolute;
    background: {cloud_color};
    width: 80px;
    height: 80px;
    top: -45px;
    right: 25px;
    border-radius: 50%;
}}
.cloud1 {{ width: 180px; height: 55px; top: 15%; left: -30%; animation-duration: 38s; opacity: 0.85; }}
.cloud2 {{ width: 220px; height: 65px; top: 38%; left: -45%; animation-duration: 28s; opacity: 0.65; transform: scale(0.8); }}

@keyframes move {{
    0% {{ transform: translateX(0); }}
    100% {{ transform: translateX(200vw); }}
}}

.drop {{
    position: fixed;
    width: 2px;
    height: 18px;
    background: #60a5fa;
    animation: fall linear infinite;
    z-index: 0;
}}
@keyframes fall {{
    0% {{transform: translateY(-100px);}}
    100% {{transform: translateY(100vh);}}
}}

.leaf {{
    position: fixed;
    width: 14px;
    height: 14px;
    background: #22c55e;
    border-radius: 50% 0 50% 0;
    animation: fly 6s linear infinite;
    z-index: 0;
}}
@keyframes fly {{
    0% {{transform: translate(-50px,100vh) rotate(0);}}
    100% {{transform: translate(120vw,-20vh) rotate(720deg);}}
}}

/* =========================
   AUTO DARK/LIGHT TEXT
   ========================= */

/* Semua teks utama */
.main-text,
.stMarkdown,
.stMarkdown *,
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
[data-testid="stDataFrame"] *,
[data-testid="stTable"] *,
table, th, td,
h1, h2, h3, h4, h5, h6,
p, span {{
    color: {text_color} !important;
}}

/* Label widget mengikuti tema */
label,
[data-testid="stWidgetLabel"] {{
    color: {text_color} !important;
}}

/* Dropdown kota:
   label ikut tema,
   isi pilihan kota tetap hitam */
div[data-baseweb="select"] span {{
    color: black !important;
}}

div[data-baseweb="popover"] * {{
    color: black !important;
}}


</style>
""", unsafe_allow_html=True)

# =========================
# BACKGROUND ANIMATION TRIGGER
# =========================
bg = ""
if "berawan" in latest["cuaca"].lower():
    bg += "<div class='cloud cloud1'></div><div class='cloud cloud2'></div>"

if "hujan" in latest["cuaca"].lower():
    bg += "".join([
        f"<div class='drop' style='left:{i*2}%;animation-duration:{0.4+(i%5)*0.2}s'></div>"
        for i in range(60)
    ])

if latest["angin"] > 10:
    bg += "".join([
        f"<div class='leaf' style='left:{i*5}%;animation-duration:{3+(i%3)}s'></div>"
        for i in range(15)
    ])

st.markdown(bg, unsafe_allow_html=True)

# =========================
# DASHBOARD
# =========================
if menu == "🏠 Dashboard":
    st.markdown("<h2 class='main-text'>🌦️ Prediksi Cuaca BMKG</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='city-title'>📍 {kota}</div>", unsafe_allow_html=True)
    st.markdown(f"<h3 class='main-text'>🌤️ {latest['cuaca']}</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"<div class='card'><h3>🌡 Suhu</h3><h1>{latest['suhu']}°C</h1></div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='card'><h3>💧 Kelembapan</h3><h1>{latest['kelembapan']}%</h1></div>", unsafe_allow_html=True)

    with col3:
        st.markdown(f"<div class='card'><h3>🌬 Angin</h3><h1>{latest['angin']} km/j</h1></div>", unsafe_allow_html=True)

# =========================
# DATASET
# =========================
elif menu == "📊 Dataset":
    st.markdown("<h2 class='main-text'>📊 Dataset BMKG</h2>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)
    st.write(df.describe())

# =========================
# PREDIKSI
# =========================
elif menu == "🔮 Prediksi":

    st.markdown(
        f"<h1 class='main-text'>🌦️ Prediksi Cuaca BMKG - Kawasan {kota}</h1>",
        unsafe_allow_html=True
    )

    col_left, col_right = st.columns([1, 2.4])

    with col_left:
        st.markdown(
        "<h3 class='main-text'>⚙️ Atur Parameter Simulasi</h3>",
        unsafe_allow_html=True
        )

        tanggal_target = st.date_input(
            "Pilih Tanggal Prediksi",
            datetime.now().date()
        )

        jam = st.slider(
            "Jam Target",
            0,
            23,
            12
        )

        hu = st.number_input(
            "Kelembapan (%)",
            min_value=40,
            max_value=100,
            value=70
        )

        ws = st.number_input(
            "Kecepatan Angin (km/j)",
            min_value=0.0,
            max_value=50.0,
            value=2.6
        )

        prediksi_btn = st.button("🔍 Hitung Prediksi")

    with col_right:

        if prediksi_btn:

            daily_predictions = []
            cuaca_list = []
            kategori_list = []

            for h in range(24):

                factor = (12 - abs(12 - h)) / 12

                simulated_hu = max(
                    40.0,
                    min(100.0, hu - (factor * 15))
                )

                simulated_ws = max(
                    0.0,
                    ws + (factor * 4)
                )

                input_daily = pd.DataFrame(
                    [[h, simulated_hu, simulated_ws]],
                    columns=[
                        "jam",
                        "kelembapan",
                        "angin"
                    ]
                )

                suhu = rf_model.predict(
                    input_daily
                )[0]

                daily_predictions.append(suhu)

                # Kategori suhu
                if suhu < 27:
                    kategori = "Sejuk"
                    cuaca = "☁️ Berawan"

                elif suhu <= 30:
                    kategori = "Hangat"
                    cuaca = "🌤️ Cerah Berawan"

                else:
                    kategori = "Panas"
                    cuaca = "☀️ Cerah"

                cuaca_list.append(cuaca)
                kategori_list.append(kategori)

            df_daily = pd.DataFrame({
                "Jam": range(24),
                "Waktu": [
                    f"{i:02d}:00 WIB"
                    for i in range(24)
                ],
                "Suhu Prediksi (°C)": [
                    round(x, 2)
                    for x in daily_predictions
                ],
                "Cuaca": cuaca_list,
                "Kategori": kategori_list
            })

            st.markdown(
            "<h3 class='main-text'>📅 Estimasi Prediksi Harian Dinamis (24 Jam)</h3>",
            unsafe_allow_html=True
            )

            st.dataframe(
                df_daily,
                use_container_width=True,
                height=520
            )

    if prediksi_btn:

        rata2 = sum(daily_predictions)/24
        maksimum = max(daily_predictions)
        minimum = min(daily_predictions)

        if rata2 < 27:
            kategori_harian = "Sejuk"

        elif rata2 <= 30:
            kategori_harian = "Hangat"

        else:
            kategori_harian = "Panas"

        st.markdown("---")
        st.markdown(
        "<h3 class='main-text'>📊 Rata-rata Suhu Harian dan Kategori Cuaca</h3>",
        unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns([1, 3, 1])

        with c1:

            st.metric(
                "🌡️ Rata-rata Suhu Harian",
                f"{rata2:.2f} °C"
            )

            st.metric(
                "☀️ Suhu Maksimum",
                f"{maksimum:.2f} °C"
            )

            st.metric(
                "🌙 Suhu Minimum",
                f"{minimum:.2f} °C"
            )

        with c2:

            progress = min(
                max(
                    (rata2 - minimum) /
                    (maksimum - minimum + 0.01),
                    0
                ),
                1
            )

            st.progress(progress)

            st.markdown(
                f"""
                <center>
                </center>
                """,
                unsafe_allow_html=True
            )

        with c3:

            st.metric(
                "🌤️ Estimasi Cuaca",
                kategori_harian
            )

# =========================
# EVALUASI
# =========================
elif menu == "📈 Evaluasi":

    st.markdown("<h2 class='main-text'>📈 Evaluasi Model</h2>", unsafe_allow_html=True)

    # =====================
    # HITUNG MAPE
    # =====================
    rf_pred_test = rf_model.predict(X_test)
    xgb_pred_test = xgb_model.predict(X_test)

    rf_mape = mean_absolute_percentage_error(y_test, rf_pred_test) * 100
    xgb_mape = mean_absolute_percentage_error(y_test, xgb_pred_test) * 100

    # =====================
    # METRIC CARD
    # =====================
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "🌳 Random Forest MAPE",
            f"{rf_mape:.2f}%"
        )

    with col2:
        st.metric(
            "⚡ XGBoost MAPE",
            f"{xgb_mape:.2f}%"
        )

    # =====================
    # TABEL PERBANDINGAN
    # =====================
    st.markdown(
    "<h3 class='main-text'>📊 Perbandingan Nilai MAPE</h3>",
    unsafe_allow_html=True
    )
    hasil_mape = pd.DataFrame({
        "Model": ["Random Forest", "XGBoost"],
        "MAPE (%)": [
            round(rf_mape, 2),
            round(xgb_mape, 2)
        ]
    })


    terbaik = hasil_mape.loc[
        hasil_mape["MAPE (%)"].idxmin()
    ]

    st.success(
        f"🏆 Model terbaik adalah {terbaik['Model']} "
        f"dengan MAPE {terbaik['MAPE (%)']:.2f}%"
    )

    # =====================
    # DATA EVALUASI
    # =====================
    df_eval = df.copy()

    df_eval["rf_prediksi"] = rf_model.predict(
        df_eval[["jam", "kelembapan", "angin"]]
    )

    df_eval["xgb_prediksi"] = xgb_model.predict(
        df_eval[["jam", "kelembapan", "angin"]]
    )

    # =====================
    # GRAFIK
    # =====================
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_eval["datetime"],
        y=df_eval["suhu"],
        mode='lines+markers',
        name='Aktual BMKG'
    ))

    fig.add_trace(go.Scatter(
        x=df_eval["datetime"],
        y=df_eval["rf_prediksi"],
        mode='lines+markers',
        name='Random Forest'
    ))

    fig.add_trace(go.Scatter(
        x=df_eval["datetime"],
        y=df_eval["xgb_prediksi"],
        mode='lines+markers',
        name='XGBoost'
    ))

    fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    hovermode="x unified",
    autosize=True,

    font=dict(
        color=text_color
    ),

    legend=dict(
        font=dict(
            color=text_color
        )
    ),

    xaxis=dict(
        title_font=dict(color=text_color),
        tickfont=dict(color=text_color)
    ),

    yaxis=dict(
        title_font=dict(color=text_color),
        tickfont=dict(color=text_color)
    )
    )

    st.plotly_chart(fig, use_container_width=True)
