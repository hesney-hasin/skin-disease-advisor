

# Skin Disease Advisor

AI-powered skin disease detection web application built with **FastAPI**, **Gradio**, and an **EfficientNet-B3** image classification model. The app analyzes a skin image, predicts the most likely condition, shows top predictions with confidence scores, and provides recommendation, next steps, and care tips.

## Live Links

- **Live App:** https://hesneyhasin-skin-disease-advisor.hf.space/
- **API Docs (Swagger):** https://hesneyhasin-skin-disease-advisor.hf.space/docs
- **API Health Check:** https://hesneyhasin-skin-disease-advisor.hf.space/health


##  Real Demo Output

```
Benign Keratosis-like Lesions (BKL)
Confidence: 52.5%
SEVERITY: LOW-MODERATE CONFIDENCE

 TOP PREDICTIONS
1. Benign Keratosis-like Lesions (BKL) 52.5%
2. Warts, Molluscum & Viral Infections 19.6%
3. Melanocytic Nevi (NV) 9.9%
4. Seborrheic Keratoses & Benign Tumors 5.0%
5. Atopic Dermatitis 4.7%

 ABOUT
Non-cancerous skin growths including seborrheic keratoses and solar lentigines. 
Very common in older adults and are harmless.

 SYMPTOMS
Waxy, stuck-on appearing growths. Brown, black, or tan colored. 
Can be flat or slightly raised with a scaly surface.

RECOMMENDED ACTION
• AI detected Benign Keratosis-like Lesions (BKL) — preliminary screening only.
• Do not self-medicate based on this result.
• Consult a licensed dermatologist for accurate diagnosis.
```


## Features

- Upload skin image → AI analysis in seconds
- **Top 5 predictions** with confidence bars
- **Severity color-coding** (LOW/GREEN, MODERATE/YELLOW, HIGH/RED)
- **LLM-powered recommendations** via Google Gemini
- **Interactive Swagger API docs** at `/docs`
- **Production health checks** at `/health`


## Supported Backend Endpoints

### `GET /`

```json
{"message": "API running. Visit /docs"}
```


### `GET /health`

```json
{
  "status": "healthy",
  "model_loaded": true
}
```


### `POST /analyze-skin`

**Input**: Image file
**Output**: Disease prediction + top 5 + LLM recommendations

## How to Use

**🌐 Live App** (30 seconds):

1. https://hesneyhasin-skin-disease-advisor.hf.space/
2. Upload image → **Analyze** → instant results

**🔧 Test API**:

1. https://hesneyhasin-skin-disease-advisor.hf.space/docs
2. **POST /analyze-skin** → Try it out → upload → Execute

## Tech Stack

```
Frontend:  Gradio + Custom CSS
Backend:   FastAPI + Pydantic
Model:     EfficientNet-B3 
LLM:       Google Gemini API
Deploy:    Hugging Face Docker Space
Image:     Pillow + OpenCV
```


## Project Structure

```
.
├── app/
│   ├── main.py          # FastAPI routes
│   ├── model.py         # EfficientNet classifier
│   ├── llm.py           # Gemini recommendations
│   ├── schemas.py       
│   └── utils.py
├── ui/gradio_app.py     # Gradio frontend
├── models/efficientnet_skin.pth
├── requirements.txt
├── Dockerfile
└── README.md
```




## 🎥 Demonstration Video

**[YouTube/Vimeo link goes here after recording]**

***



