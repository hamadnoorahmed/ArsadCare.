import streamlit as st

# 1. إعدادات الصفحة (يجب استدعاؤها مرة واحدة فقط في البداية)
st.set_page_config(
    page_title="أرصاد-كير | ArsadCare",
    page_icon="🌪️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import joblib
import numpy as np
import os
from mock_data import CITIES_DATA
from recommender import get_smart_recommendations

# ---------------------------------------------------------
# تنسيق CSS احترافي لتعريب المحاذاة وضبط الاتجاهات والنصوص
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* 1. ضبط الاتجاه العام للواجهة ليكون لليمين */
    .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 2. محاذاة العناوين والنصوص لليمين */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        text-align: right !important;
        direction: rtl !important;
    }

    /* 3. محاذاة عناصر القائمة الجانبية (Sidebar) */
    section[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    section[data-testid="stSidebar"] * {
        text-align: right !important;
    }

    /* إخفاء السايدبار عند الإغلاق بدون ترك بقايا نصية */
    section[data-testid="stSidebar"][aria-expanded="false"] {
        display: none !important;
    }

    /* 4. تصميم بطاقات المؤشرات الرقمية النظيفة */
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 14px 18px;
        border-radius: 12px;
        text-align: right;
        direction: rtl;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .metric-value-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        direction: rtl;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: bold;
        color: #f8fafc;
        direction: ltr; /* لضمان عدم انقلاب الأرقام والوحدات */
        display: inline-block;
    }

    /* 5. تنسيق التوجيهات والقوائم */
    .custom-bullet {
        margin-bottom: 10px;
        font-size: 0.95rem;
        line-height: 1.6;
        direction: rtl;
        text-align: right;
    }
    .vulnerable-pill {
        display: inline-block;
        background-color: #334155;
        color: #f8fafc;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 3px 2px;
        direction: rtl;
    }
    </style>
""", unsafe_allow_html=True)

# 2. تحميل نموذج الذكاء الاصطناعي
@st.cache_resource
def load_ml_model():
    if os.path.exists("phri_model.pkl"):
        return joblib.load("phri_model.pkl")
    return None

ml_model = load_ml_model()

# 3. القائمة الجانبية (Sidebar)
st.sidebar.title("🎛️ لوحة القيادة والتحكم")
st.sidebar.markdown("**منظومة أرصاد-كير (ArsadCare)**")

selected_city = st.sidebar.selectbox("اختر المدينة / النطاق الجغرافي:", list(CITIES_DATA.keys()))
city_base = CITIES_DATA[selected_city]

st.sidebar.divider()
st.sidebar.subheader("🔬 وضع المحاكاة التفاعلية (What-If)")
simulate = st.sidebar.checkbox("تفعيل محاكاة ظاهرة متطرفة", value=False)

if simulate:
    st.sidebar.caption("غيّر قراءات الطقس لاختبار استجابة الذكاء الاصطناعي اللحظية:")
    temp_input = st.sidebar.slider("درجة الحرارة (°م)", 15.0, 52.0, float(city_base["temperature_c"]))
    hum_input = st.sidebar.slider("الرطوبة النسبية (%)", 5.0, 95.0, float(city_base["humidity_pct"]))
    pm10_input = st.sidebar.slider("كثافة الغبار PM10 (µg/m³)", 20.0, 500.0, float(city_base["pm10_ug_m3"]))
    wind_input = st.sidebar.slider("سرعة الرياح (كم/س)", 5.0, 70.0, float(city_base["wind_speed_kmh"]))
else:
    temp_input = float(city_base["temperature_c"])
    hum_input = float(city_base["humidity_pct"])
    pm10_input = float(city_base["pm10_ug_m3"])
    wind_input = float(city_base["wind_speed_kmh"])

# 4. التنبؤ بالذكاء الاصطناعي والحسابات
if ml_model is not None:
    input_features = np.array([[temp_input, hum_input, pm10_input, wind_input]])
    prediction = ml_model.predict(input_features)[0]
    calculated_phri = round(float(prediction[0]), 1)
    calculated_surge = round(float(prediction[1]), 1)
    ai_status_badge = "🟢 نموذج الذكاء الاصطناعي (ML Active)"
else:
    calculated_phri = city_base["phri_score"]
    calculated_surge = city_base["projected_er_surge_pct"]
    ai_status_badge = "🟡 الوضع الافتراضي (Mock Active)"

# استدعاء محرك التوصيات المنطقي المطور
guidance = get_smart_recommendations(calculated_phri, temp_input, pm10_input, hum_input, wind_input)
calculated_risk = guidance["calculated_risk"]

# 5. الواجهة الرئيسية
st.title(f"منظومة التنبؤ بالأثر الصحي - {selected_city}")
st.caption(f"المنطقة الفرعية: {city_base['zone_name']} | حالة المعالجة: {ai_status_badge}")

# 6. بطاقات المؤشرات النظيفة والمصممة خصيصاً للتغلب على مشاكل الاتجاه والألوان
col1, col2, col3, col4 = st.columns(4)

risk_badge_colors = {
    "CRITICAL": "#dc2626",  # أحمر ناصع
    "HIGH":     "#ea580c",  # برتقالي
    "MODERATE": "#d97706",  # أصفر/ذهبي
    "LOW":      "#16a34a"   # أخضر
}
badge_color = risk_badge_colors.get(calculated_risk, "#16a34a")

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">درجة الحرارة</div>
            <div class="metric-value" style="text-align: right; width: 100%;">
                {temp_input} <span style="font-size: 1rem; color: #94a3b8;">°م</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">تركيز الغبار (PM10)</div>
            <div class="metric-value" style="text-align: right; width: 100%;">
                {pm10_input} <span style="font-size: 0.9rem; color: #94a3b8;">µg/m³</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">مؤشر الخطر الصحي (PHRI)</div>
            <div class="metric-value-container">
                <span class="metric-value">
                    {calculated_phri} <span style="font-size: 0.95rem; color: #64748b;">/ 100</span>
                </span>
                <span style="background-color: {badge_color}; color: #ffffff; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; letter-spacing: 0.5px;">
                    {calculated_risk}
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">ضغط الطوارئ المتوقع</div>
            <div class="metric-value" style="text-align: right; width: 100%;">
                +{calculated_surge}%
            </div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# 7. الخريطة والرسوم البيانية
col_map, col_chart = st.columns([1, 1])

with col_map:
    st.subheader("📍 الخارطة الجغرافية وتحديد نطاق الخطر")
    m = folium.Map(location=[city_base["lat"], city_base["lon"]], zoom_start=11)
    
    pin_color = "red" if calculated_risk == "CRITICAL" else "orange" if calculated_risk == "HIGH" else "green"
    
    folium.Marker(
        [city_base["lat"], city_base["lon"]],
        popup=f"{selected_city}: {calculated_risk}",
        tooltip=f"PHRI Score: {calculated_phri}",
        icon=folium.Icon(color=pin_color, icon="info-sign")
    ).add_to(m)
    
    st_folium(m, width=500, height=350)

with col_chart:
    st.subheader("📈 توقعات مسار الخطر خلال 24 ساعة")
    hours = [f"+{i}h" for i in range(2, 26, 4)]
    trend = [max(5, min(100, calculated_phri + (i * 2.2 if i < 3 else -i * 1.8))) for i in range(len(hours))]
    
    df_trend = pd.DataFrame({"الوقت": hours, "مستوى الخطر": trend})
    fig = px.line(df_trend, x="الوقت", y="مستوى الخطر", markers=True)
    fig.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# 8. قسم التوجيهات الميدانية والطبية
st.subheader("🤖 توجيهات غرف القيادة والتحكم الميدانية")

st.warning(guidance["summary"])

col_hosp, col_field = st.columns(2)

with col_hosp:
    st.markdown("### 🏥 إجراءات المستشفيات والكوادر الصحية:")
    for action in guidance["hospital_actions"]:
        st.markdown(f"<div class='custom-bullet'>✅ {action}</div>", unsafe_allow_html=True)

with col_field:
    st.markdown("### 🚑 التنبيهات الميدانية والجهات الخارجية:")
    st.markdown(f"**إجراء السلامة المهنية:** {guidance['field_advisory']}")
    st.markdown("**الفئات المعرضة للخطر في هذا السيناريو:**")
    
    pills_html = "".join([f"<span class='vulnerable-pill'>{group}</span>" for group in guidance["vulnerable_groups"]])
    st.markdown(f"<div style='margin-top: 8px;'>{pills_html}</div>", unsafe_allow_html=True)
