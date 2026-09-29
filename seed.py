import json

from database import Base, SessionLocal, engine
from models import HealthRule


RULES = [
    {
        "condition_id": "hypertension",
        "condition_name": "Hypertension (High BP)",
        "high_risk_ingredients": [
            "sodium",
            "salt",
            "monosodium glutamate",
            "msg",
            "sodium benzoate",
        ],
        "warning": "High sodium or salt content may be a concern for people managing blood pressure.",
        "substitutions": {
            "salt": "Herbal seasonings or lemon juice",
            "sodium": "Herbs, spices, or lemon juice",
            "monosodium glutamate": "Herbs, spices, or umami-rich vegetables",
            "msg": "Herbs, spices, or umami-rich vegetables",
            "sodium benzoate": "A preservative-free alternative where appropriate",
        },
    },
    {
        "condition_id": "type_2_diabetes",
        "condition_name": "Type 2 Diabetes",
        "high_risk_ingredients": [
            "sugar",
            "high fructose corn syrup",
            "dextrose",
            "maltodextrin",
            "sucrose",
        ],
        "warning": "Added or rapidly absorbed sugars may be a concern for blood-glucose management.",
        "substitutions": {
            "sugar": "Stevia, erythritol, or monk fruit extract",
            "high fructose corn syrup": "Unsweetened alternatives",
            "dextrose": "A lower-sugar alternative",
            "maltodextrin": "A lower-glycemic alternative where appropriate",
            "sucrose": "Stevia, erythritol, or monk fruit extract",
        },
    },
    {
        "condition_id": "celiac_or_gluten",
        "condition_name": "Celiac / Gluten Intolerance",
        "high_risk_ingredients": [
            "wheat",
            "barley",
            "rye",
            "malt",
            "semolina",
            "spelt",
        ],
        "warning": "This ingredient can contain gluten and may be unsuitable for people avoiding gluten.",
        "substitutions": {
            "wheat": "Almond flour or certified gluten-free oat flour",
            "barley": "Certified gluten-free grains",
            "rye": "Certified gluten-free grains",
            "malt": "A certified gluten-free malt alternative",
            "semolina": "Corn flour or certified gluten-free flour",
            "spelt": "Certified gluten-free flour",
        },
    },
    {
        "condition_id": "lactose_intolerance",
        "condition_name": "Lactose Intolerance",
        "high_risk_ingredients": [
            "milk",
            "lactose",
            "whey",
            "casein",
            "butter",
            "cream",
            "milk solids",
        ],
        "warning": "This ingredient is a dairy or lactose-related ingredient and may cause problems for people with lactose intolerance.",
        "substitutions": {
            "milk": "Almond milk, oat milk, or soy milk",
            "lactose": "A lactose-free alternative",
            "whey": "A plant-based protein alternative",
            "casein": "A plant-based protein alternative",
            "butter": "Olive oil or a dairy-free butter alternative",
            "cream": "Coconut cream or another dairy-free alternative",
            "milk solids": "A dairy-free milk powder alternative",
        },
    },
]


def seed_health_rules() -> None:
    """Create or update the default health rules."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for rule in RULES:
            existing = (
                db.query(HealthRule)
                .filter(HealthRule.condition_id == rule["condition_id"])
                .first()
            )

            values = {
                "condition_name": rule["condition_name"],
                "high_risk_ingredients": json.dumps(rule["high_risk_ingredients"]),
                "warning": rule["warning"],
                "substitutions": json.dumps(rule["substitutions"]),
            }

            if existing:
                for key, value in values.items():
                    setattr(existing, key, value)
            else:
                db.add(
                    HealthRule(
                        condition_id=rule["condition_id"],
                        **values,
                    )
                )

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_health_rules()
    print("Health rules seeded/updated.")
