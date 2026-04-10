import io
import gradio as gr
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from app.model import SkinDiseaseClassifier
from app.llm import get_llm_recommendations
from app.schemas import SkinAnalysisResponse, HealthResponse
   

app = FastAPI(
    title="Skin Disease Detection & LLM Advisor",
    version="1.0.0",
    description="EfficientNet-B3 skin disease classifier with Gemini LLM recommendations"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

classifier = SkinDiseaseClassifier()

@app.on_event("startup")
async def startup():
    classifier.load_model("models/efficientnet_skin.pth")

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    return HealthResponse(status="healthy", model_loaded=classifier.is_loaded)

@app.post("/analyze-skin", response_model=SkinAnalysisResponse, tags=["Prediction"])
async def analyze_skin(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image.")
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(422, "Cannot decode image.")
    disease, confidence, top5 = classifier.predict(image)
    recs = get_llm_recommendations(disease, confidence)
    return SkinAnalysisResponse(
        disease=disease,
        confidence=round(confidence, 4),
        top_predictions=top5,
        recommendations=recs["recommendations"],
        next_steps=recs["next_steps"],
        tips=recs["tips"],
    )