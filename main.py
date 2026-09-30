import json
import requests

from typing import List

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
)
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel, Field

from rapidfuzz import fuzz, process

from sqlalchemy.orm import Session

from database import Base, engine, get_db

from models import (
    Analysis,
    HealthRule,
    User,
    UserCondition,
)

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


# =========================================================
# DATABASE SETUP
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="NutriScan AI",
    version="1.0.0"
)


# =========================================================
# STATIC FILES
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


templates = Jinja2Templates(
    directory="templates"
)


# =========================================================
# AUTHENTICATION
# =========================================================

security = HTTPBearer(
    auto_error=False
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Read the JWT from the Authorization header
    and return the logged-in user.
    """

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    token = credentials.credentials

    try:
        user_id = decode_access_token(token)

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found."
        )

    return user


# =========================================================
# REQUEST MODELS
# =========================================================

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AnalysisRequest(BaseModel):
    conditions: List[str] = Field(
        default_factory=list
    )

    ingredients: List[str] = Field(
        default_factory=list
    )


class HealthConditionRequest(BaseModel):
    condition_ids: List[str] = Field(
        default_factory=list
    )


# =========================================================
# HOME PAGE
# =========================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )


# =========================================================
# GET ALL AVAILABLE HEALTH CONDITIONS
# =========================================================

@app.get("/api/conditions")
def get_conditions(
    db: Session = Depends(get_db)
):

    rules = (
        db.query(HealthRule)
        .order_by(HealthRule.id)
        .all()
    )

    return [
        {
            "id": rule.condition_id,
            "name": rule.condition_name
        }
        for rule in rules
    ]


# =========================================================
# REGISTER USER
# =========================================================

@app.post("/api/auth/register")
def register_user(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):

    name = user_data.name.strip()
    email = user_data.email.strip().lower()
    password = user_data.password

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Name is required."
        )

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Email is required."
        )

    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters."
        )

    # -----------------------------------------------------
    # CHECK EXISTING USER
    # -----------------------------------------------------

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists."
        )

    # -----------------------------------------------------
    # HASH PASSWORD
    # -----------------------------------------------------

    hashed_password = hash_password(password)

    # -----------------------------------------------------
    # CREATE USER
    # -----------------------------------------------------

    new_user = User(
        name=name,
        email=email,
        password_hash=hashed_password
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {
        "message": "Registration successful.",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }


# =========================================================
# LOGIN USER
# =========================================================

@app.post("/api/auth/login")
def login_user(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):

    email = login_data.email.strip().lower()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    # -----------------------------------------------------
    # CHECK USER
    # -----------------------------------------------------

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    # -----------------------------------------------------
    # VERIFY PASSWORD
    # -----------------------------------------------------

    if not verify_password(
        login_data.password,
        user.password_hash
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    # -----------------------------------------------------
    # CREATE JWT
    # -----------------------------------------------------

    access_token = create_access_token(
        user.id
    )

    return {
        "message": "Login successful.",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


# =========================================================
# GET CURRENT LOGGED-IN USER
# =========================================================

@app.get("/api/auth/me")
def get_me(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }


# =========================================================
# GET CURRENT USER'S HEALTH CONDITIONS
# =========================================================

@app.get("/api/health/conditions")
def get_my_conditions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user_conditions = (
        db.query(UserCondition)
        .filter(
            UserCondition.user_id == current_user.id
        )
        .all()
    )

    condition_ids = [
        item.condition_id
        for item in user_conditions
    ]

    return {
        "user_id": current_user.id,
        "conditions": condition_ids
    }


# =========================================================
# SAVE CURRENT USER'S HEALTH CONDITIONS
# =========================================================

@app.put("/api/health/conditions")
def save_my_conditions(
    payload: HealthConditionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # REMOVE DUPLICATES
    # -----------------------------------------------------

    condition_ids = list(
        dict.fromkeys(
            payload.condition_ids
        )
    )

    # -----------------------------------------------------
    # VALIDATE CONDITION IDS
    # -----------------------------------------------------

    if condition_ids:

        valid_rules = (
            db.query(HealthRule)
            .filter(
                HealthRule.condition_id.in_(
                    condition_ids
                )
            )
            .all()
        )

        valid_condition_ids = {
            rule.condition_id
            for rule in valid_rules
        }

        invalid_condition_ids = [
            condition_id
            for condition_id in condition_ids
            if condition_id not in valid_condition_ids
        ]

        if invalid_condition_ids:

            raise HTTPException(
                status_code=400,
                detail={
                    "message": "One or more health conditions are invalid.",
                    "invalid_conditions": invalid_condition_ids
                }
            )

    # -----------------------------------------------------
    # DELETE OLD USER CONDITIONS
    # -----------------------------------------------------

    (
        db.query(UserCondition)
        .filter(
            UserCondition.user_id == current_user.id
        )
        .delete(
            synchronize_session=False
        )
    )

    # -----------------------------------------------------
    # ADD NEW USER CONDITIONS
    # -----------------------------------------------------

    for condition_id in condition_ids:

        new_condition = UserCondition(
            user_id=current_user.id,
            condition_id=condition_id
        )

        db.add(new_condition)

    db.commit()

    return {
        "message": "Health conditions saved successfully.",
        "conditions": condition_ids
    }


# =========================================================
# ANALYZE FOOD
# =========================================================

@app.post("/api/analyze")
def analyze_food(
    payload: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # VALIDATE INGREDIENTS
    # -----------------------------------------------------

    if not payload.ingredients:

        raise HTTPException(
            status_code=400,
            detail="Please enter at least one ingredient."
        )

    # -----------------------------------------------------
    # CLEAN CONDITIONS
    # -----------------------------------------------------

    selected_conditions = set(
        payload.conditions
    )

    # -----------------------------------------------------
    # IF USER DID NOT SEND CONDITIONS,
    # USE THE USER'S SAVED CONDITIONS
    # -----------------------------------------------------

    if not selected_conditions:

        saved_conditions = (
            db.query(UserCondition)
            .filter(
                UserCondition.user_id
                == current_user.id
            )
            .all()
        )

        selected_conditions = {
            condition.condition_id
            for condition in saved_conditions
        }

    # -----------------------------------------------------
    # CLEAN INGREDIENTS
    # -----------------------------------------------------

    ingredients = []

    for ingredient in payload.ingredients:

        cleaned = ingredient.lower().strip()

        if cleaned and cleaned not in ingredients:

            ingredients.append(cleaned)

    if not ingredients:

        raise HTTPException(
            status_code=400,
            detail="Please enter at least one valid ingredient."
        )

    # -----------------------------------------------------
    # GET SELECTED HEALTH RULES
    # -----------------------------------------------------

    rules = (
        db.query(HealthRule)
        .filter(
            HealthRule.condition_id.in_(
                selected_conditions
            )
        )
        .all()
    )

    # -----------------------------------------------------
    # FIND FLAGGED INGREDIENTS
    # -----------------------------------------------------

    flagged_items = []

    substitutions = {}

    flagged_ingredient_names = set()

    for rule in rules:

        try:

            high_risk_ingredients = json.loads(
                rule.high_risk_ingredients
            )

        except Exception:

            high_risk_ingredients = []

        try:

            rule_substitutions = json.loads(
                rule.substitutions
            )

        except Exception:

            rule_substitutions = {}

        for ingredient in ingredients:

            if not high_risk_ingredients:
                continue

            match = process.extractOne(
                ingredient,
                high_risk_ingredients,
                scorer=fuzz.partial_ratio
            )

            if match and match[1] >= 80:

                matched_rule = match[0]

                duplicate = any(
                    item["ingredient"] == ingredient
                    and item["condition_triggered"]
                    == rule.condition_name
                    for item in flagged_items
                )

                if duplicate:
                    continue

                flagged_items.append(
                    {
                        "ingredient": ingredient,
                        "condition_triggered":
                            rule.condition_name,
                        "matched_rule":
                            matched_rule,
                        "warning":
                            rule.warning
                    }
                )

                flagged_ingredient_names.add(
                    ingredient
                )

                if matched_rule in rule_substitutions:

                    substitutions[ingredient] = (
                        rule_substitutions[
                            matched_rule
                        ]
                    )

    # =====================================================
    # SAFETY SCORE
    # =====================================================

    total_ingredients = len(
        ingredients
    )

    total_flagged = len(
        flagged_ingredient_names
    )

    if total_ingredients == 0:

        safety_score = 100

    else:

        safety_score = round(
            (
                (
                    total_ingredients
                    - total_flagged
                )
                / total_ingredients
            )
            * 100
        )

    # =====================================================
    # STATUS
    # =====================================================

    if total_flagged == 0:

        status = "No Detected Concern"

    elif safety_score >= 70:

        status = "Potential Concern"

    elif safety_score >= 40:

        status = "Multiple Potential Concerns"

    else:

        status = "Significant Potential Concerns"

    # =====================================================
    # SAVE ANALYSIS FOR THIS USER
    # =====================================================

    analysis = Analysis(

        user_id=current_user.id,

        conditions=json.dumps(
            list(selected_conditions)
        ),

        ingredients=json.dumps(
            ingredients
        ),

        safety_score=safety_score,

        status=status,

        flagged_ingredients=json.dumps(
            flagged_items
        ),

        suggested_substitutions=json.dumps(
            substitutions
        )
    )

    db.add(analysis)

    db.commit()

    db.refresh(analysis)

    # =====================================================
    # RETURN RESULT
    # =====================================================

    return {

        "id": analysis.id,

        "safety_score":
            safety_score,

        "status":
            status,

        "flagged_ingredients":
            flagged_items,

        "suggested_substitutions":
            substitutions
    }


# =========================================================
# ANALYSIS HISTORY FOR CURRENT USER
# =========================================================

@app.get("/api/history")
def history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    rows = (
        db.query(Analysis)
        .filter(
            Analysis.user_id
            == current_user.id
        )
        .order_by(
            Analysis.created_at.desc()
        )
        .limit(20)
        .all()
    )

    return [

        {
            "id":
                row.id,

            "conditions":
                json.loads(
                    row.conditions
                ),

            "ingredients":
                json.loads(
                    row.ingredients
                ),

            "safety_score":
                row.safety_score,

            "status":
                row.status,

            "created_at":
                (
                    row.created_at.isoformat()
                    if row.created_at
                    else None
                )
        }

        for row in rows
    ]


# =========================================================
# OPEN FOOD FACTS PRODUCT LOOKUP
# =========================================================

@app.get("/api/product/{barcode}")
def get_product(
    barcode: str
):

    url = (
        "https://world.openfoodfacts.org/"
        f"api/v3/product/{barcode}.json"
    )

    headers = {
        "User-Agent": "NutriScanAI/1.0"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException:

        raise HTTPException(
            status_code=502,
            detail="Could not connect to Open Food Facts."
        )

    # -----------------------------------------------------
    # PRODUCT NOT FOUND
    # -----------------------------------------------------

    if data.get("status") != "success":

        raise HTTPException(
            status_code=404,
            detail="Product was not found in Open Food Facts."
        )

    product = data.get(
        "product",
        {}
    )

    nutriments = product.get(
        "nutriments",
        {}
    )

    # -----------------------------------------------------
    # RETURN PRODUCT INFORMATION
    # -----------------------------------------------------

    return {

        "product_name":
            product.get(
                "product_name",
                ""
            ),

        "brands":
            product.get(
                "brands",
                ""
            ),

        "barcode":
            barcode,

        "ingredients":
            product.get(
                "ingredients_text",
                ""
            ),

        "allergens":
            product.get(
                "allergens",
                ""
            ),

        "categories":
            product.get(
                "categories",
                ""
            ),

        "nutrition": {

            "energy_kcal":
                nutriments.get(
                    "energy-kcal_100g"
                ),

            "sugars_g":
                nutriments.get(
                    "sugars_100g"
                ),

            "carbohydrates_g":
                nutriments.get(
                    "carbohydrates_100g"
                ),

            "fat_g":
                nutriments.get(
                    "fat_100g"
                ),

            "saturated_fat_g":
                nutriments.get(
                    "saturated-fat_100g"
                ),

            "protein_g":
                nutriments.get(
                    "proteins_100g"
                ),

            "fiber_g":
                nutriments.get(
                    "fiber_100g"
                ),

            "salt_g":
                nutriments.get(
                    "salt_100g"
                ),

            "sodium_g":
                nutriments.get(
                    "sodium_100g"
                )
        }
    }