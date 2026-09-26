# app.py
import streamlit as st
st.set_page_config(initial_sidebar_state="expanded")
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import joblib
import numpy as np
import os
from mock_data import CITIES_DATA
from recommender import get_smart_recommendations

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="أرصاد-كير | ArsadCare",
    page_icon="🌪️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تنسيق CSS لمنع تداخل الأرقام والرموز وضبط القوائم العربية
st.markdown("""
    <style>
    .stApp { direction: rtl; }
    html, body, [class*="css"] {
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    div[data-testid="metric-container"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 15px;
        border-radius: 10px;
        white-space: nowrap;
    }
    div[data-testid="metric-container"] label {
        font-size: 0.9rem !important;
    }
    .custom-bullet {
        margin-bottom: 8px;
        font-size: 1rem;
        line-height: 1.6;
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

# 6. بطاقات المؤشرات النظيفة بصرياً
# 6. بطاقات المؤشرات النظيفة والمصممة خصيصاً للتغلب على مشاكل الاتجاه والألوان
col1, col2, col3, col4 = st.columns(4)

# قاموس ألوان الشارات حسب مستوى الخطر
risk_badge_colors = {
    "CRITICAL": "#dc2626",  # أحمر ناصع
    "HIGH":     "#ea580c",  # برتقالي
    "MODERATE": "#d97706",  # أصفر/ذهبي
    "LOW":      "#16a34a"   # أخضر
}
badge_color = risk_badge_colors.get(calculated_risk, "#16a34a")

with col1:
    st.markdown(f"""
        <div style="background-color: #1e293b; border: 1px solid #334155; padding: 14px; border-radius: 10px;">
            <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600;">درجة الحرارة</div>
            <div style="font-size: 1.6rem; font-weight: bold; color: #f8fafc; margin-top: 4px; direction: ltr; text-align: right;">
                {temp_input} <span style="font-size: 1rem; color: #94a3b8;">°م</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style="background-color: #1e293b; border: 1px solid #334155; padding: 14px; border-radius: 10px;">
            <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600;">تركيز الغبار (PM10)</div>
            <div style="font-size: 1.6rem; font-weight: bold; color: #f8fafc; margin-top: 4px; direction: ltr; text-align: right;">
                {pm10_input} <span style="font-size: 0.9rem; color: #94a3b8;">µg/m³</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div style="background-color: #1e293b; border: 1px solid #334155; padding: 14px; border-radius: 10px;">
            <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600;">مؤشر الخطر الصحي (PHRI)</div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px;">
                <span style="font-size: 1.6rem; font-weight: bold; color: #f8fafc; direction: ltr;">
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
        <div style="background-color: #1e293b; border: 1px solid #334155; padding: 14px; border-radius: 10px;">
            <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600;">ضغط الطوارئ المتوقع</div>
            <div style="font-size: 1.6rem; font-weight: bold; color: #f8fafc; margin-top: 4px; direction: ltr; text-align: right;">
                +{calculated_surge}%
            </div>
        </div>
    """, unsafe_allow_html=True)

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

# 8. قسم التوجيهات الميدانية والطبية بدون نقاط مزدوجة
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
    for group in guidance["vulnerable_groups"]:
        st.badge(group)
