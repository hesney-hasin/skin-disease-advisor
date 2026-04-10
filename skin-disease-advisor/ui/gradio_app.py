import io
import gradio as gr
from PIL import Image
import requests
import json
import os

API_URL = os.environ.get("API_URL", "http://0.0.0.0:7860")

DISEASE_INFO = {
    "Eczema": {
        "severity": "LOW-MEDIUM",
        "color": "f59e0b",
        "about": "Eczema is a chronic inflammatory skin condition causing dry, itchy, and inflamed patches. It often appears on the hands, feet, face, and behind the knees.",
        "symptoms": "Red, inflamed, dry, and itchy skin. May include small bumps, flaking, cracking, or oozing. Scratching can worsen symptoms."
    },
    "Warts, Molluscum & Viral Infections": {
        "severity": "LOW",
        "color": "10b981",
        "about": "Viral skin infections caused by HPV (warts) or poxvirus (molluscum). They produce small, raised bumps on the skin and are contagious through direct contact.",
        "symptoms": "Small, rough, skin-colored bumps (warts) or dome-shaped, pearly papules with central dimple (molluscum). Usually painless."
    },
    "Melanoma": {
        "severity": "HIGH",
        "color": "ef4444",
        "about": "Melanoma is the most dangerous form of skin cancer, arising from pigment-producing melanocytes. Early detection is critical for survival.",
        "symptoms": "Asymmetric moles with irregular borders, multiple colors (brown, black, red, white, blue), diameter > 6mm, or evolving size/shape/color."
    },
    "Atopic Dermatitis": {
        "severity": "LOW-MEDIUM",
        "color": "f59e0b",
        "about": "A chronic form of eczema common in children but can persist into adulthood. Often associated with allergies and asthma (atopic triad).",
        "symptoms": "Intense itching, red or brownish-gray patches, dry/cracked/scaly skin. In infants, often appears on the face and scalp."
    },
    "Basal Cell Carcinoma (BCC)": {
        "severity": "HIGH",
        "color": "ef4444",
        "about": "The most common type of skin cancer. It grows slowly and rarely metastasizes but can cause significant local tissue destruction if untreated.",
        "symptoms": "Pearly or waxy bump, flat flesh-colored or brown scar-like lesion, or a bleeding/scabbing sore that heals and recurs."
    },
    "Melanocytic Nevi (NV)": {
        "severity": "LOW",
        "color": "10b981",
        "about": "Commonly known as moles. These are benign growths of melanocytes. Most are harmless but some may develop into melanoma over time.",
        "symptoms": "Small, evenly colored brown, tan, or black spots on the skin. Usually round or oval with smooth borders."
    },
    "Benign Keratosis-like Lesions (BKL)": {
        "severity": "LOW",
        "color": "10b981",
        "about": "Non-cancerous skin growths including seborrheic keratoses and solar lentigines. Very common in older adults and are harmless.",
        "symptoms": "Waxy, stuck-on appearing growths. Brown, black, or tan colored. Can be flat or slightly raised with a scaly surface."
    },
    "Psoriasis & Lichen Planus": {
        "severity": "MEDIUM",
        "color": "f59e0b",
        "about": "Psoriasis is a chronic autoimmune condition causing rapid skin cell turnover. Lichen planus is an inflammatory condition affecting skin and mucous membranes.",
        "symptoms": "Thick, red patches covered with silvery scales (psoriasis). Purplish, flat-topped, itchy bumps (lichen planus). May affect nails and joints."
    },
    "Seborrheic Keratoses & Benign Tumors": {
        "severity": "LOW",
        "color": "10b981",
        "about": "Non-cancerous skin growths that appear with age. They can look concerning but are completely harmless and do not require treatment.",
        "symptoms": "Waxy, scaly, slightly raised growths. Range from light tan to dark brown or black. Often described as having a 'pasted on' appearance."
    },
    "Tinea, Ringworm & Fungal Infections": {
        "severity": "LOW-MEDIUM",
        "color": "f59e0b",
        "about": "Fungal infections of the skin caused by dermatophytes. Highly contagious through direct contact or contaminated surfaces. Common in warm, moist environments.",
        "symptoms": "Red, itchy, scaly, or raised patches often in ring shapes. Blisters or oozing may occur. Commonly affects feet (athlete's foot), groin (jock itch), and scalp."
    },
}

DEFAULT_RESULT_HTML = """
<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px 20px;margin-bottom:12px;">
    <div style="font-size:1.25rem;font-weight:700;color:#f0f6fc;margin-bottom:4px;">🔬 Waiting for Analysis</div>
    <div style="font-size:0.85rem;color:#8b949e;">Upload an image and click Analyze to get results.</div>
</div>
<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px 20px;margin-bottom:12px;">
    <div style="font-size:0.75rem;letter-spacing:0.5px;text-transform:uppercase;color:#6e7681;font-weight:600;">TOP PREDICTIONS</div>
</div>
<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px 20px;margin-bottom:12px;">
    <div style="font-size:0.75rem;letter-spacing:0.5px;text-transform:uppercase;color:#6e7681;font-weight:600;margin-bottom:10px;">📖 ABOUT</div>
    <p style="font-size:0.9rem;margin:0;line-height:1.5;color:#f0f6fc;">No information available.</p>
</div>
<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px 20px;margin-bottom:12px;">
    <div style="font-size:0.75rem;letter-spacing:0.5px;text-transform:uppercase;color:#6e7681;font-weight:600;margin-bottom:10px;">🩹 SYMPTOMS</div>
    <p style="font-size:0.9rem;margin:0;line-height:1.5;color:#f0f6fc;">N/A</p>
</div>
<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px 20px;margin-bottom:12px;">
    <div style="font-size:0.75rem;letter-spacing:0.5px;text-transform:uppercase;color:#6e7681;font-weight:600;margin-bottom:10px;">✅ RECOMMENDED ACTION</div>
    <div style="background:rgba(255,255,255,0.03);border:1px solid #30363d;border-radius:6px;padding:12px;font-size:0.9rem;line-height:1.5;color:#f0f6fc;">
       -
    </div>
</div>
<div style="background:rgba(153,27,27,0.1);border-radius:8px;padding:16px 20px;border:1px solid rgba(153,27,27,0.3);color:#fca5a5;font-size:0.8rem;text-align:center;line-height:1.5;">
    ⚠ This tool is for educational purposes only and is NOT a substitute for professional medical advice. Always consult a qualified dermatologist.
</div>
"""


def build_result_html(data: dict) -> str:
    disease = data.get("disease", "Unknown")
    confidence = data.get("confidence", 0)
    predictions = data.get("top_predictions", [])

    info = DISEASE_INFO.get(disease, {})
    severity = info.get("severity", "UNKNOWN")
    sev_color = info.get("color", "94a3b8")
    about = info.get("about", data.get("about", "No information available."))
    symptoms = info.get("symptoms", data.get("symptoms", "N/A"))

    recs_raw = data.get("recommendations", "Consult a doctor.")
    if isinstance(recs_raw, list):
        recommendations = "<br>".join(f"• {r}" for r in recs_raw)
    else:
        recommendations = recs_raw

    # Confidence tier
    pct = confidence * 100
    if pct >= 80:
        conf_label, conf_color = "HIGH CONFIDENCE", "10b981"
    elif pct >= 50:
        conf_label, conf_color = "MODERATE CONFIDENCE", "f59e0b"
    else:
        conf_label, conf_color = "LOW CONFIDENCE", "ef4444"

    # Build predictions HTML
    preds_html = ""
    for i, p in enumerate(predictions):
        p_disease = p.get("disease", "Unknown")
        p_conf = p.get("confidence", 0)
        prefix = "👑 " if i == 0 else f"{i+1}. "
        bar_bg = "linear-gradient(90deg, #8b5cf6, #3b82f6)" if i == 0 else "#3b82f6"
        preds_html += f"""
        <div style="margin-bottom:10px;">
            <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#8b949e;margin-bottom:4px;">
                <span>{prefix}{p_disease}</span>
                <strong style="color:#f0f6fc;">{p_conf*100:.1f}%</strong>
            </div>
            <div style="background:#1c2128;border-radius:4px;height:6px;overflow:hidden;">
                <div style="height:100%;border-radius:4px;width:{p_conf*100:.1f}%;background:{bar_bg};"></div>
            </div>
        </div>
        """

    html = f"""
    <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px 20px;margin-bottom:12px;">
        <div style="font-size:1.25rem;font-weight:700;color:#f0f6fc;margin-bottom:4px;">🔬 {disease}</div>
        <div style="font-size:0.85rem;color:#8b949e;margin-bottom:16px;">
            Confidence: <strong style="color:#f0f6fc;">{pct:.1f}%</strong>
        </div>
        <div style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap;">
            <span style="display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:20px;font-size:0.7rem;font-weight:600;letter-spacing:0.5px;border:1px solid #{sev_color};color:#{sev_color};">
                <span style="width:8px;height:8px;border-radius:50%;background:#{sev_color};display:inline-block;"></span>
                SEVERITY: {severity}
            </span>
            <span style="display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:20px;font-size:0.7rem;font-weight:600;letter-spacing:0.5px;border:1px solid #{conf_color};color:#{conf_color};">
                <span style="width:8px;height:8px;border-radius:50%;background:#{conf_color};display:inline-block;"></span>
                {conf_label}
            </span>
        </div>
        <div style="font-size:0.75rem;letter-spacing:0.5px;text-transform:uppercase;color:#6e7681;font-weight:600;margin-bottom:10px;">
            TOP PREDICTIONS
        </div>
        {preds_html}
    </div>

    <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px 20px;margin-bottom:12px;">
        <div style="font-size:0.75rem;letter-spacing:0.5px;text-transform:uppercase;color:#6e7681;font-weight:600;margin-bottom:10px;">📖 ABOUT</div>
        <p style="font-size:0.9rem;margin:0;line-height:1.5;color:#f0f6fc;">{about}</p>
    </div>

    <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px 20px;margin-bottom:12px;">
        <div style="font-size:0.75rem;letter-spacing:0.5px;text-transform:uppercase;color:#6e7681;font-weight:600;margin-bottom:10px;">🩹 SYMPTOMS</div>
        <p style="font-size:0.9rem;margin:0;line-height:1.5;color:#f0f6fc;">{symptoms}</p>
    </div>

    <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px 20px;margin-bottom:12px;">
        <div style="font-size:0.75rem;letter-spacing:0.5px;text-transform:uppercase;color:#6e7681;font-weight:600;margin-bottom:10px;">✅ RECOMMENDED ACTION</div>
        <div style="background:rgba(255,255,255,0.03);border:1px solid #30363d;border-radius:6px;padding:12px;font-size:0.9rem;line-height:1.5;color:#f0f6fc;">
            {recommendations}
        </div>
    </div>

    <div style="background:rgba(153,27,27,0.1);border-radius:8px;padding:16px 20px;border:1px solid rgba(153,27,27,0.3);color:#fca5a5;font-size:0.8rem;text-align:center;line-height:1.5;">
        ⚠ This tool is for educational purposes only and is NOT a substitute for professional medical advice. Always consult a qualified dermatologist for diagnosis and treatment.
    </div>
    """
    return html


def analyze_image(image):
    if image is None:
        return DEFAULT_RESULT_HTML

    try:
        buf = io.BytesIO()
        if isinstance(image, Image.Image):
            image.save(buf, format="PNG")
        else:
            Image.fromarray(image).save(buf, format="PNG")
        buf.seek(0)

        resp = requests.post(
            f"{API_URL}/analyze-skin",
            files={"file": ("image.png", buf, "image/png")},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return build_result_html(data)

    except Exception as e:
        return f"""
        <div style="background:rgba(153,27,27,0.15);border:1px solid rgba(153,27,27,0.4);border-radius:8px;padding:20px;color:#fca5a5;text-align:center;">
            <div style="font-size:1.2rem;margin-bottom:8px;">❌ Analysis Failed</div>
            <div style="font-size:0.85rem;">{str(e)}</div>
        </div>
        """


# ── Gradio UI ──────────────────────────────────────────────
with gr.Blocks(
    title="Skin Disease Advisor",
    css="""
    .gradio-container { background: #0d1117 !important; max-width: 1100px !important; }
    .gr-button { font-family: 'Inter', sans-serif !important; }
    """
) as demo:

    gr.HTML("""
    <div style="background:linear-gradient(180deg,#1e3a8a 0%,#172554 100%);border-radius:12px;padding:30px 20px;text-align:center;margin-bottom:24px;box-shadow:0 4px 6px -1px rgba(0,0,0,0.5);">
        <h1 style="font-size:2rem;font-weight:700;color:#fff;margin:0;display:flex;align-items:center;justify-content:center;gap:10px;">
            🩺 Skin Disease Advisor
        </h1>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=4):
            image_input = gr.Image(
                label="📷 Upload Skin Image",
                type="pil",
                height=280,
            )

            analyze_btn = gr.Button(
                "🔍 Analyze Image",
                variant="primary",
                size="lg",
            )

            gr.HTML("""
            <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;margin-top:12px;">
                <div style="font-size:0.75rem;letter-spacing:0.5px;text-transform:uppercase;color:#6e7681;margin-bottom:12px;font-weight:600;">
                    DETECTS THESE CONDITIONS
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px 12px;font-size:0.8rem;color:#8b949e;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="width:8px;height:8px;border-radius:50%;background:#ef4444;flex-shrink:0;"></span> Melanoma
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="width:8px;height:8px;border-radius:50%;background:#ef4444;flex-shrink:0;"></span> Basal Cell Carcinoma
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="width:8px;height:8px;border-radius:50%;background:#f59e0b;flex-shrink:0;"></span> Eczema
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="width:8px;height:8px;border-radius:50%;background:#f59e0b;flex-shrink:0;"></span> Atopic Dermatitis
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="width:8px;height:8px;border-radius:50%;background:#f59e0b;flex-shrink:0;"></span> Psoriasis
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="width:8px;height:8px;border-radius:50%;background:#f59e0b;flex-shrink:0;"></span> Tinea Ringworm
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="width:8px;height:8px;border-radius:50%;background:#10b981;flex-shrink:0;"></span> Melanocytic Nevi
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="width:8px;height:8px;border-radius:50%;background:#10b981;flex-shrink:0;"></span> Warts
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="width:8px;height:8px;border-radius:50%;background:#10b981;flex-shrink:0;"></span> Seborrheic Keratoses
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="width:8px;height:8px;border-radius:50%;background:#10b981;flex-shrink:0;"></span> Benign Lesions
                    </div>
                </div>
            </div>
            """)

        with gr.Column(scale=5):
            result_html = gr.HTML(DEFAULT_RESULT_HTML)

    analyze_btn.click(
        fn=analyze_image,
        inputs=image_input,
        outputs=result_html,
    )

    image_input.clear(
        fn=lambda: DEFAULT_RESULT_HTML,
        inputs=None,
        outputs=result_html,
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
