import gradio as gr
import requests
import json
from PIL import Image
import io
import os

API_URL = os.environ.get("API_URL", "http://localhost:7860")

DISEASE_INFO = {
    "1. Eczema":                                              {"severity": "LOW-MEDIUM",  "color": "ffbb00"},
    "10. Warts Molluscum and other Viral Infections":       {"severity": "LOW",         "color": "00aa44"},
    "2. Melanoma":                                          {"severity": "HIGH",        "color": "ff4444"},
    "3. Atopic Dermatitis":                                {"severity": "LOW-MEDIUM",  "color": "ffbb00"},
    "4. Basal Cell Carcinoma (BCC)":                          {"severity": "MEDIUM-HIGH", "color": "ff8800"},
    "5. Melanocytic Nevi (NV)":                             {"severity": "LOW",         "color": "00aa44"},
    "6. Benign Keratosis-like Lesions (BKL)":                 {"severity": "LOW",         "color": "00aa44"},
    "7. Psoriasis pictures Lichen Planus and related diseases":{"severity": "LOW-MEDIUM", "color": "ffbb00"},
    "8. Seborrheic Keratoses and other Benign Tumors":      {"severity": "LOW",         "color": "00aa44"},
    "9. Tinea Ringworm Candidiasis and other Fungal Infections":{"severity": "LOW-MEDIUM","color": "ffbb00"},
}

SEVERITY_DOT = {
    "LOW":         "00aa44",
    "LOW-MEDIUM":  "ffbb00",
    "MEDIUM-HIGH": "ff8800",
    "HIGH":        "ff4444",
    "UNKNOWN":     "888888",
}


CSS = """
* { box-sizing: border-box; }

.gradio-container {
    max-width: 1100px !important;
    margin: 0 auto !important;
    font-family: 'Segoe UI', sans-serif !important;
}

.app-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 16px;
    padding: 32px;
    text-align: center;
    margin-bottom: 24px;
    border: 1px solid #0f3460;
}

.app-header h1 {
    color: #ffffff !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    margin: 0 0 8px 0 !important;
    letter-spacing: -0.5px;
}

.app-header p {
    color: #94a3b8 !important;
    font-size: 1rem !important;
    margin: 0 !important;
}

.result-card {
    background: #1e293b;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #334155;
    margin-bottom: 16px;
}

.disease-name {
    font-size: 1.5rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 4px;
}

.confidence-text {
    font-size: 1rem;
    color: #94a3b8;
    margin-bottom: 16px;
}

.severity-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 16px;
}

.bar-container {
    margin: 6px 0;
}

.bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;
    color: #cbd5e1;
    margin-bottom: 4px;
}

.bar-track {
    background: #334155;
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #3b82f6, #06b6d4);
    transition: width 0.5s ease;
}

.bar-fill-top {
    background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
}

.info-section {
    background: #1e293b;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #334155;
    margin-bottom: 12px;
}

.info-section h3 {
    color: #e2e8f0 !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0 0 10px 0 !important;
    opacity: 0.7;
}

.info-section p {
    color: #cbd5e1 !important;
    font-size: 0.95rem !important;
    margin: 0 !important;
    line-height: 1.6 !important;
}

.action-box {
    border-radius: 10px;
    padding: 14px 18px;
    font-weight: 600;
    font-size: 0.95rem;
    margin-top: 12px;
}

.disclaimer {
    background: #1e1e2e;
    border: 1px solid #ff444433;
    border-radius: 10px;
    padding: 12px 16px;
    color: #ff8888 !important;
    font-size: 0.82rem !important;
    text-align: center;
    margin-top: 16px;
}

.upload-area {
    border-radius: 12px !important;
    border: 2px dashed #334155 !important;
}

.analyze-btn {
    background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 14px !important;
    color: white !important;
    cursor: pointer !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}

.analyze-btn:hover { opacity: 0.9 !important; }

.empty-state {
    text-align: center;
    padding: 48px 24px;
    color: #475569;
    font-size: 0.95rem;
}

.empty-state .icon { font-size: 3rem; margin-bottom: 12px; }
"""

def build_result_html(data):
    disease         = data.get("disease", "Unknown")
    confidence      = data.get("confidence", 0) * 100
    top5            = data.get("top_predictions", [])
    recommendations = data.get("recommendations", ["Consult a licensed dermatologist."])
    next_steps      = data.get("next_steps", ["Book an appointment with a dermatologist."])
    tips            = data.get("tips", ["Keep the area clean and moisturized."])

    # Still use DISEASE_INFO for severity + color ONLY
    info     = DISEASE_INFO.get(disease, {})
    severity = info.get("severity", "UNKNOWN")
    color    = info.get("color", "888888")

    def to_list_html(items):
        if isinstance(items, list):
            return "".join(f"<li style='margin-bottom:6px'>• {i}</li>" for i in items)
        return f"<li>• {items}</li>"

    # Top predictions bars
    bars_html = ""
    for i, p in enumerate(top5):
        pct   = p["confidence"] * 100
        name  = p["disease"]
        extra = "bar-fill-top" if i == 0 else ""
        bars_html += f"""
        <div class="bar-container">
            <div class="bar-label">
                <span>{"👑 " if i == 0 else f"{i+1}. "}{name}</span>
                <span><b>{pct:.1f}%</b></span>
            </div>
            <div class="bar-track">
                <div class="bar-fill {extra}" style="width:{pct:.1f}%"></div>
            </div>
        </div>"""

    html = f"""
    <div class="result-card">
        <div class="disease-name">🔬 {disease}</div>
        <div class="confidence-text">Confidence: <b>{confidence:.1f}%</b></div>
        <div class="severity-badge" style="background:{color}22; color:{color}; border:1px solid {color}55">
            {severity}
        </div>
        <div style="margin-top:16px">
            <div style="font-size:0.8rem;color:#64748b;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:10px;font-weight:600">TOP PREDICTIONS</div>
            {bars_html}
        </div>
    </div>

    <div class="info-section">
        <h3>📖 About</h3>
        <p>{about}</p>
    </div>

    <div class="info-section">
        <h3>🩹 Symptoms</h3>
        <p>{symptoms}</p>
    </div>

    <div class="info-section">
        <h3>✅ Recommended Action</h3>
        <div class="action-box" style="background:{color}22; color:{color}; border:1px solid {color}44">
            {action}
        </div>
    </div>

    <div class="disclaimer">
        ⚠️ This tool is for educational purposes only and is NOT a substitute for professional medical advice.
        Always consult a qualified dermatologist for diagnosis and treatment.
    </div>
    """
    return html

def analyze_image(image):
    if image is None:
        return """<div class="empty-state">
            <div class="icon">🩺</div>
            <div>Upload a skin image and click <b>Analyze</b> to get started</div>
        </div>"""

    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    buf.seek(0)

    try:
        resp = requests.post(
            f"{API_URL}/analyze-skin",
            files={"file": ("image.jpg", buf, "image/jpeg")},
            timeout=30
        )
        data = resp.json()
    except Exception as e:
        return f"""<div class="result-card" style="border-color:#ff4444">
            <div style="color:#ff4444;font-weight:700">❌ Connection Error</div>
            <div style="color:#94a3b8;margin-top:8px">Could not reach the API.<br><code>{e}</code></div>
        </div>"""

    return build_result_html(data)

with gr.Blocks(css=CSS, title="Skin Disease Advisor", theme=gr.themes.Base()) as demo:

    gr.HTML("""
    <div class="app-header">
        <h1>🩺 Skin Disease Advisor</h1>
        <p>AI-powered skin disease detection </p>
    </div>
    """)

    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            image_input = gr.Image(
                type="pil",
                label="Upload Skin Image",
                elem_classes=["upload-area"],
                height=320
            )
            analyze_btn = gr.Button(
                "🔍 Analyze Image",
                variant="primary",
                elem_classes=["analyze-btn"]
            )
            gr.HTML("""
            <div style="margin-top:12px; padding:12px; background:#1e293b;
                        border-radius:10px; border:1px solid #334155">
                <div style="font-size:0.8rem; color:#64748b; font-weight:600;
                             text-transform:uppercase; letter-spacing:0.05em; margin-bottom:8px">
                    Detects These Conditions
                </div>
                <div style="font-size:0.82rem; color:#94a3b8; line-height:1.8">
                    🔴 Melanoma &nbsp;|&nbsp; 🔴 Basal Cell Carcinoma<br>
                    🟡 Eczema &nbsp;|&nbsp; 🟡 Atopic Dermatitis<br>
                    🟡 Psoriasis &nbsp;|&nbsp; 🟡 Tinea Ringworm<br>
                    🟢 Melanocytic Nevi &nbsp;|&nbsp; 🟢 Warts<br>
                    🟢 Seborrheic Keratoses &nbsp;|&nbsp; 🟢 Benign Lesions
                </div>
            </div>
            """)

        with gr.Column(scale=1):
            result_html = gr.HTML("""
            <div class="empty-state">
                <div class="icon">🩺</div>
                <div>Upload a skin image and click <b>Analyze</b> to get started</div>
            </div>
            """)

    analyze_btn.click(
        fn=analyze_image,
        inputs=image_input,
        outputs=result_html
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
