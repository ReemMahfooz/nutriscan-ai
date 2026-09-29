import json
import re
from pathlib import Path
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from rapidfuzz import fuzz, process
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Analysis, HealthRule
from seed import seed_health_rules


# Always resolve project files relative to this file, not the terminal's cwd.
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Create the tables and make sure the default health rules exist.
Base.metadata.create_all(bind=engine)
seed_health_rules()

app = FastAPI(title="NutriScan AI", version="1.0.0")

# This is required so /static/app.js and /static/style.css are served.
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


class AnalysisRequest(BaseModel):
    conditions: List[str] = Field(default_factory=list)
    ingredients: List[str] = Field(default_factory=list)


def normalize(text: str) -> str:
    """Lowercase text and normalize punctuation/whitespace."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def contains_phrase(text: str, phrase: str) -> bool:
    """Match a phrase only on word boundaries."""
    text_n = normalize(text)
    phrase_n = normalize(phrase)
    if not text_n or not phrase_n:
        return False
    return re.search(rf"\b{re.escape(phrase_n)}\b", text_n) is not None


# Common ingredients that contain a risky word but are normally different
# ingredients. These prevent obvious false positives from partial matching.
SAFE_EXCEPTIONS = {
    "wheat": {"buckwheat"},
    "milk": {"almond milk", "oat milk", "soy milk", "coconut milk", "cashew milk"},
    "butter": {"peanut butter", "almond butter", "cashew butter", "sunflower butter"},
}


def find_match(ingredient: str, targets: list[str]):
    """Find a risk ingredient using exact/token matching plus conservative fuzzy matching."""
    ingredient_n = normalize(ingredient)

    # First prefer exact phrase/token matches.
    for target in targets:
        target_n = normalize(target)
        if target_n in SAFE_EXCEPTIONS and ingredient_n in SAFE_EXCEPTIONS[target_n]:
            continue
        if contains_phrase(ingredient, target):
            return target, 100.0

    # Fuzzy matching is intentionally conservative. It catches small typos such
    # as "sodum" -> "sodium" without making words like "batter" -> "butter".
    words = ingredient_n.split()
    for target in targets:
        target_n = normalize(target)
        if target_n in SAFE_EXCEPTIONS and ingredient_n in SAFE_EXCEPTIONS[target_n]:
            continue

        if " " in target_n:
            # For multi-word rules, compare the whole normalized ingredient.
            score = fuzz.ratio(ingredient_n, target_n)
            if score >= 90:
                return target, score
        else:
            for word in words:
                score = fuzz.ratio(word, target_n)
                if score >= 88:
                    return target, score

    return None


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request},
    )


@app.get("/api/conditions")
def get_conditions(db: Session = Depends(get_db)):
    rules = db.query(HealthRule).order_by(HealthRule.id).all()
    return [{"id": r.condition_id, "name": r.condition_name} for r in rules]


@app.post("/api/analyze")
def analyze_food(payload: AnalysisRequest, db: Session = Depends(get_db)):
    if not payload.ingredients:
        raise HTTPException(status_code=400, detail="Please enter at least one ingredient.")

    selected = set(payload.conditions)
    raw_ingredients = [i.strip() for i in payload.ingredients if i.strip()]

    rules = db.query(HealthRule).filter(HealthRule.condition_id.in_(selected)).all()
    flagged_items = []
    substitutions = {}
    total_penalty = 0

    for rule in rules:
        targets = json.loads(rule.high_risk_ingredients)
        rule_substitutions = json.loads(rule.substitutions)

        for ingredient in raw_ingredients:
            match = find_match(ingredient, targets)
            if not match:
                continue

            matched_rule, _score = match
            flagged_items.append(
                {
                    "ingredient": ingredient,
                    "condition_triggered": rule.condition_name,
                    "matched_rule": matched_rule,
                    "warning": rule.warning,
                }
            )
            total_penalty += 25

            # Support both the canonical risk ingredient and a longer user
            # ingredient (e.g. wheat -> wheat flour).
            replacement = rule_substitutions.get(matched_rule)
            if replacement:
                substitutions[ingredient] = replacement

    safety_score = max(0, 100 - total_penalty)
    if safety_score > 85:
        status = "Safe Choice"
    elif safety_score >= 50:
        status = "Moderate Caution"
    else:
        status = "High Risk Alert"

    analysis = Analysis(
        conditions=json.dumps(list(selected)),
        ingredients=json.dumps(raw_ingredients),
        safety_score=safety_score,
        status=status,
        flagged_ingredients=json.dumps(flagged_items),
        suggested_substitutions=json.dumps(substitutions),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {
        "id": analysis.id,
        "safety_score": safety_score,
        "status": status,
        "flagged_ingredients": flagged_items,
        "suggested_substitutions": substitutions,
    }


@app.get("/api/history")
def history(db: Session = Depends(get_db)):
    rows = db.query(Analysis).order_by(Analysis.created_at.desc()).limit(20).all()
    return [
        {
            "id": row.id,
            "conditions": json.loads(row.conditions),
            "ingredients": json.loads(row.ingredients),
            "safety_score": row.safety_score,
            "status": row.status,
            # created_at is stored as UTC. Add Z so the browser converts it to
            # the user's local timezone instead of treating UTC as local time.
            "created_at": row.created_at.isoformat() + "Z" if row.created_at else None,
        }
        for row in rows
    ]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
