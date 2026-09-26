# recommender.py

def evaluate_risk_level(phri_score: float, temp: float, dust: float, humidity: float, wind: float) -> str:
    """
    دالة منطقية تضمن عدم إغفال الحالات المتطرفة حتى لو كان الموديل الخطّي يعطي درجة منخفضة.
    """
    # 1. شروط الطوارئ القصوى الحادة (Emergency Override)
    if temp >= 48.0 or dust >= 300.0 or (temp >= 42.0 and humidity >= 70.0):
        return "CRITICAL"
    
    # 2. شروط الخطر العالي
    if temp >= 40.0 or dust >= 180.0 or wind >= 50.0:
        return "HIGH" if phri_score < 80 else "CRITICAL"

    # 3. الاعتماد على الموديل في الظروف الاعتيادية
    if phri_score < 30:
        return "LOW"
    elif phri_score < 60:
        return "MODERATE"
    elif phri_score < 80:
        return "HIGH"
    else:
        return "CRITICAL"


def get_smart_recommendations(phri_score: float, temp: float, dust: float, humidity: float, wind: float):
    # حساب مستوى الخطر الفعلي بدمج الذكاء الاصطناعي مع القواعد الميدانية
    actual_risk = evaluate_risk_level(phri_score, temp, dust, humidity, wind)

    if actual_risk == "CRITICAL":
        if dust >= 200.0:
            summary = "🚨 موجة غبارية حادة جداً: انعدام في الرؤية واختناق تنفسي ناتج عن كثافة الجسيمات PM10."
            hospital_actions = [
                "رفع الجاهزية القصوى لأقسام العناية التنفسية والطوارئ بنسبة 40%.",
                "تأمين مخزون استثنائي من موسعات الشعب الهوائية وأقنعة الترشيح عالية الكفاءة.",
                "استدعاء الفرق الطبية المساندة لمواجهة تدفق حالات أزمات الربو الحادة."
            ]
            field_advisory = "إلزامية تعليق كافة الأنشطة الإنشائية وحظر العمل الميداني في المناطق المفتوحة فوراً."
            vulnerable = ["مرضى الربو والحساسية", "كبار السن", "العمالة الميدانية", "مرضى القلب"]
        else:
            summary = "🚨 موجة حرارية شديدة الخطورة: درجات حرارة قياسية ترفع احتمالية ضربات الشمس والإجهاد الحراري."
            hospital_actions = [
                "تجهيز وحدات التبريد السريع ومحاليل الإنعاش الوريدي في غرف الطوارئ.",
                "استنفار الكوادر لمتابعة حالات الفشل الكلوي الحاد الناتج عن الجفاف الشديد.",
                "تخصيص مسارات سريعة لنقل ومعالجة حالات الإعياء الحراري الميداني."
            ]
            field_advisory = "حظر التعرض المباشر للشمس ومنع العمل في الأماكن المفتوحة تحت طائلة المساءلة."
            vulnerable = ["العمال الميدانيون", "الأطفال", "كبار السن", "ممارسو الرياضة الخارجية"]

    elif actual_risk == "HIGH":
        summary = "⚠️ تقلبات جوية قاسية: تزايد الضغط التشغيلي على أقسام الإسعاف والطوارئ."
        hospital_actions = [
            "رفع جاهزية أقسام الطوارئ بنسبة 20% وتفقد أجهزة التبخير والأوكسجين.",
            "إعادة توزيع مناوبات التمريض لتغطية ساعات الذروة المتوقعة."
        ]
        field_advisory = "تقليص فترات التعرض للأنشطة الخارجية وارتداء الكمامات الوقائية عند الخروج."
        vulnerable = ["مرضى الجهاز التنفسي", "ضعاف المناعة"]

    elif actual_risk == "MODERATE":
        summary = "🟡 ظروف مناخية تقلبة معتدلة: تسبب إجهاداً خفيفاً لبعض الفئات الأكثر عرضة."
        hospital_actions = [
            "استمرار العمليات التشغيلية الاعتيادية مع مراقبة معدلات التدفق على الطوارئ."
        ]
        field_advisory = "تنبيه الفئات الحساسة بتوخي الحذر وتجنب التعرض المباشر للتقلبات الجوية."
        vulnerable = ["مصابو الحساسية الموسمية"]

    else:
        summary = "🟢 أجواء مناخية مستقرة: القراءات ضمن الحدود الطبيعية الآمنة لصحة المجتمع."
        hospital_actions = [
            "العمليات التشغيلية في مستوياتها المعتادة دون الحاجة لإجراءات استثنائية."
        ]
        field_advisory = "الظروف مثالية لكافة الأنشطة الخارجية دون محاذير صحية."
        vulnerable = ["لا توجد فئات معرضة الخطر"]

    return {
        "calculated_risk": actual_risk,
        "summary": summary,
        "hospital_actions": hospital_actions,
        "field_advisory": field_advisory,
        "vulnerable_groups": vulnerable
    }