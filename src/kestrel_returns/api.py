import pandas as pd
import joblib
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List, Dict, Any

from kestrel_returns.features import REQUIRED_FEATURES
from kestrel_returns.reasons import generate_reasons

ARTIFACTS_DIR = Path(__file__).parent.parent.parent / "artifacts"
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Kestrel Returns API")

class PredictionRequest(BaseModel):
    # Required features
    family: str = Field(..., description="Product family")
    sales_channel: str
    payment_mode: str
    is_gift: str
    shield_member: str
    discount_pct: float = Field(ge=0, le=100)
    promised_delivery_days: float = Field(ge=0)
    customer_prior_orders: float = Field(ge=0)
    customer_prior_returns: float = Field(ge=0)

    # Optional field echoed back
    order_id: Optional[str] = None

    # Allow extra fields (which will be ignored)
    model_config = ConfigDict(extra='allow')

    @field_validator('customer_prior_returns')
    @classmethod
    def check_returns_le_orders(cls, v, info):
        if 'customer_prior_orders' in info.data and v > info.data['customer_prior_orders']:
            raise ValueError('customer_prior_returns cannot be greater than customer_prior_orders')
        return v

    @field_validator('family')
    @classmethod
    def check_family_enum(cls, v):
        valid = ["Air Fryer", "Ceiling Fan", "Induction Cooktop", "Mixer Grinder", "Robot Vacuum", "Room Heater", "Water Purifier"]
        if v not in valid:
            raise ValueError(f'family must be one of {valid}')
        return v

    @field_validator('sales_channel')
    @classmethod
    def check_sales_channel(cls, v):
        valid = ["app", "web", "marketplace", "partner_outlet"]
        if v not in valid:
            raise ValueError(f'sales_channel must be one of {valid}')
        return v

    @field_validator('payment_mode')
    @classmethod
    def check_payment_mode(cls, v):
        valid = ["prepaid_upi", "prepaid_card", "cod", "emi"]
        if v not in valid:
            raise ValueError(f'payment_mode must be one of {valid}')
        return v

pipeline = None
model_meta = None

@app.on_event("startup")
async def load_model():
    global pipeline, model_meta
    model_path = ARTIFACTS_DIR / "model.joblib"
    meta_path = ARTIFACTS_DIR / "model_meta.json"

    if not model_path.exists() or not meta_path.exists():
        return

    pipeline = joblib.load(model_path)
    with open(meta_path, "r") as f:
        model_meta = json.load(f)

@app.get("/health")
async def health():
    if pipeline is None or model_meta is None:
        return {"status": "unhealthy", "message": "Model artifact not found or could not be loaded."}

    return {
        "status": "healthy",
        "model_version": model_meta.get("model_version"),
        "training_window": model_meta.get("training_date_range"),
        "feature_list": model_meta.get("feature_list")
    }

@app.post("/predict")
async def predict(req: PredictionRequest):
    if pipeline is None or model_meta is None:
        raise HTTPException(status_code=503, detail="Model artifact missing or unloadable. Cannot serve predictions.")

    req_data = req.model_dump(exclude_unset=True)

    # For extra fields, model_dump doesn't automatically include them in pydantic v2 unless we use __pydantic_extra__
    if req.model_extra:
        req_data.update(req.model_extra)

    ignored_fields = []
    for k in req_data.keys():
        if k not in REQUIRED_FEATURES and k != "order_id":
            ignored_fields.append(k)

    X_row = pd.DataFrame([{k: req_data[k] for k in REQUIRED_FEATURES}])

    score = float(pipeline.predict_proba(X_row)[0, 1])

    threshold = model_meta.get("threshold", 0.112)
    recommend_call = bool(score >= threshold)

    reasons = generate_reasons(pipeline, X_row, model_meta)

    caveats = [
        "Risk probability is approximate.",
        "Customer prior field semantics have not been independently verified against the live system."
    ]

    resp = {
        "score": score,
        "recommend_call": recommend_call,
        "threshold": threshold,
        "threshold_basis": "economic break-even: Rs45 / (0.35 x Rs1150)",
        "reasons": reasons,
        "caveats": caveats,
        "ignored_fields": ignored_fields,
        "model_version": model_meta.get("model_version")
    }

    if req.order_id:
        resp["order_id"] = req.order_id

    return resp

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse(content="<h1>UI Not Found</h1>", status_code=404)
