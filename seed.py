import json

from database import Base, SessionLocal, engine
from models import HealthRule


RULES = [

    # =========================================================
    # 1. HYPERTENSION / HIGH SODIUM
    # =========================================================
    {
        "condition_id": "hypertension",
        "condition_name": "Hypertension (High BP)",

        "high_risk_ingredients": [
            "salt",
            "table salt",
            "sea salt",
            "rock salt",
            "black salt",
            "pink salt",
            "sodium",
            "sodium chloride",
            "monosodium glutamate",
            "msg",
            "sodium benzoate",
            "sodium nitrite",
            "sodium nitrate",
            "sodium bicarbonate",
            "sodium citrate",
            "sodium phosphate",
            "sodium glutamate",

            "soy sauce",
            "teriyaki sauce",
            "fish sauce",
            "oyster sauce",
            "hot sauce",
            "chili sauce",
            "pickle",
            "pickles",
            "olives",
            "papad",
            "papadum",

            "chips",
            "potato chips",
            "salted nuts",
            "salted peanuts",
            "salted popcorn",
            "namkeen",
            "pretzels",
            "crackers",

            "instant noodles",
            "instant soup",
            "canned soup",
            "packaged soup",

            "sausage",
            "sausages",
            "hot dog",
            "hot dogs",
            "bacon",
            "salami",
            "ham",
            "pepperoni",
            "deli meat",
            "processed meat",
            "cured meat",

            "frozen meal",
            "frozen meals",
            "pizza",
            "burger",
            "burgers",

            "processed cheese",
            "cheese spread",

            "bread",
            "packaged bread",

            "ketchup",
            "tomato ketchup",
            "salad dressing",
            "ready-made sauce",
            "ready-made sauces",

            "gravy",
            "instant gravy",

            "packaged snacks",
            "processed food"
        ],

        "warning": (
            "This ingredient or food may contribute significant sodium "
            "to the diet. Check the nutrition label and serving size."
        ),

        "substitutions": {
            "salt": "Herbal seasonings, lemon juice, or salt-free seasoning",
            "table salt": "Herbal seasonings or lemon juice",
            "soy sauce": "Lower-sodium soy sauce or coconut aminos",
            "ketchup": "Low-sodium or no-added-salt ketchup",
            "chips": "Unsalted nuts or fresh fruit",
            "salted nuts": "Unsalted nuts",
            "instant noodles": "Lower-sodium noodles with fresh ingredients",
            "processed meat": "Fresh, minimally processed protein",
            "papad": "Unsalted roasted alternatives"
        }
    },


    # =========================================================
    # 2. TYPE 2 DIABETES
    # =========================================================
    {
        "condition_id": "type_2_diabetes",
        "condition_name": "Type 2 Diabetes",

        "high_risk_ingredients": [
            "sugar",
            "white sugar",
            "brown sugar",
            "cane sugar",
            "cane juice",
            "sucrose",
            "glucose",
            "dextrose",
            "fructose",
            "maltose",
            "maltodextrin",

            "corn syrup",
            "high fructose corn syrup",
            "hfcs",

            "maple syrup",
            "golden syrup",
            "agave syrup",
            "honey",
            "molasses",
            "jaggery",
            "gur",
            "coconut sugar",
            "invert sugar",

            "barley malt",
            "malt syrup",
            "rice syrup",
            "caramel syrup",

            "sweetened condensed milk",
            "sweetened milk",
            "sweetened yogurt",
            "sweetened yoghurt",

            "sweetened cereal",
            "sugary cereal",
            "sweetened granola",

            "candy",
            "candies",
            "chocolate",
            "milk chocolate",

            "cookies",
            "cookie",
            "biscuits",
            "biscuit",
            "cakes",
            "cake",
            "pastries",
            "pastry",
            "donuts",
            "doughnuts",

            "ice cream",
            "kulfi",
            "sweetened dessert",
            "sweetened desserts",

            "soft drink",
            "soft drinks",
            "soda",
            "cola",
            "sweetened beverage",
            "sweetened beverages",
            "fruit drink",
            "fruit drinks",
            "sweet tea",
            "sweetened coffee",
            "energy drink",
            "energy drinks",
            "sports drink",
            "sports drinks",
            "milkshake",
            "milkshakes",
            "sweetened juice",

            "white bread",
            "white rice",
            "white pasta",
            "refined flour",
            "maida",
            "naan",
            "paratha",
            "pancakes",
            "waffles",

            "chips",
            "sweetened protein bar",
            "sweetened protein bars",
            "sweetened breakfast bar",
            "sweetened breakfast bars"
        ],

        "warning": (
            "This ingredient or food may contain added sugars or highly "
            "refined carbohydrates. Consider the serving size, total "
            "carbohydrate, and added sugar shown on the nutrition label."
        ),

        "substitutions": {
            "sugar": "Stevia, erythritol, or monk fruit extract",
            "white sugar": "A suitable non-sugar sweetener",
            "brown sugar": "A suitable non-sugar sweetener",
            "jaggery": "A suitable non-sugar sweetener",
            "gur": "A suitable non-sugar sweetener",
            "honey": "Use a suitable lower-sugar alternative",
            "soft drink": "Water or an unsweetened beverage",
            "soda": "Water or an unsweetened beverage",
            "sweetened cereal": "Unsweetened whole-grain cereal",
            "sweetened yogurt": "Unsweetened yogurt",
            "sweetened juice": "Whole fruit or an unsweetened beverage",
            "white bread": "Higher-fiber whole-grain bread",
            "white rice": "Consider a higher-fiber grain and appropriate portion",
            "maida": "Higher-fiber whole-grain flour"
        }
    },


    # =========================================================
    # 3. CELIAC / GLUTEN
    # =========================================================
    {
        "condition_id": "celiac_or_gluten",
        "condition_name": "Celiac / Gluten Intolerance",

        "high_risk_ingredients": [
            "wheat",
            "wheat flour",
            "whole wheat",
            "wheat bran",
            "wheat germ",
            "wheat starch",
            "wheat protein",
            "wheat gluten",

            "durum",
            "semolina",
            "farina",
            "spelt",
            "einkorn",
            "emmer",
            "farro",
            "graham flour",
            "khorasan",
            "kamut",

            "barley",
            "barley flour",
            "barley malt",
            "malt",
            "malt extract",
            "malt syrup",
            "malt flavoring",
            "malt vinegar",

            "rye",
            "rye flour",
            "triticale",

            "seitan",
            "couscous",
            "bulgur",
            "bulgur wheat",

            "breadcrumbs",
            "bread crumbs",
            "panko",
            "bread",
            "naan",
            "roti",
            "chapati",
            "paratha",
            "pita",
            "bagel",
            "croissant",
            "pastry",
            "cake",
            "cookie",
            "cookies",
            "biscuit",
            "biscuits",
            "cracker",
            "crackers",
            "pretzel",
            "pretzels",

            "pasta",
            "ravioli",
            "dumpling",
            "dumplings",
            "gnocchi",
            "ramen",
            "udon",
            "egg noodles",
            "chow mein",

            "soy sauce",
            "teriyaki sauce",
            "gravy",
            "roux",
            "stuffing",
            "croutons",
            "breaded foods",
            "breading",
            "flour tortilla",

            "beer",
            "malt beverage"
        ],

        "warning": (
            "This ingredient or food commonly contains or may be derived "
            "from gluten-containing grains. People with celiac disease "
            "should verify that products are certified gluten-free and "
            "consider cross-contact."
        ),

        "substitutions": {
            "wheat flour": "Certified gluten-free flour",
            "wheat": "Certified gluten-free grain or flour",
            "semolina": "Certified gluten-free alternative",
            "barley": "Rice, corn, quinoa, or another certified gluten-free grain",
            "rye": "A certified gluten-free alternative",
            "bread": "Certified gluten-free bread",
            "pasta": "Certified gluten-free pasta",
            "breadcrumbs": "Certified gluten-free breadcrumbs",
            "soy sauce": "Certified gluten-free tamari",
            "naan": "Certified gluten-free flatbread"
        }
    },


    # =========================================================
    # 4. LACTOSE INTOLERANCE
    # =========================================================
    {
        "condition_id": "lactose_intolerance",
        "condition_name": "Lactose Intolerance",

        "high_risk_ingredients": [
            "milk",
            "whole milk",
            "full cream milk",
            "skim milk",
            "low fat milk",

            "condensed milk",
            "evaporated milk",
            "milk powder",
            "skim milk powder",
            "dry milk",
            "dry milk solids",
            "milk solids",
            "nonfat dry milk",

            "milk protein",
            "milk by-products",
            "lactose",

            "whey",
            "whey powder",
            "whey protein",
            "whey concentrate",
            "whey isolate",

            "curd",
            "curds",
            "yogurt",
            "yoghurt",
            "greek yogurt",
            "greek yoghurt",
            "buttermilk",

            "cream",
            "heavy cream",
            "fresh cream",
            "sour cream",

            "ice cream",
            "kulfi",
            "milkshake",
            "milk tea",
            "milk coffee",

            "cheese",
            "cheddar",
            "mozzarella",
            "processed cheese",
            "cheese spread",
            "cream cheese",
            "cottage cheese",
            "paneer",

            "butter",
            "ghee",

            "milk chocolate",
            "milk-based chocolate",
            "milk-based dessert",
            "milk-based desserts",

            "custard",
            "pudding",
            "kheer",
            "rabri",
            "basundi",

            "milk bread",
            "milk biscuits",
            "milk-based protein powder",
            "milk-based meal replacement"
        ],

        "warning": (
            "This dairy ingredient or food may contain lactose and may "
            "cause symptoms for people with lactose intolerance. "
            "Individual tolerance can vary."
        ),

        "substitutions": {
            "milk": "Lactose-free milk or a suitable plant-based milk",
            "whole milk": "Lactose-free milk or a suitable plant-based milk",
            "milk powder": "Lactose-free milk powder where appropriate",
            "whey": "A lactose-free alternative where appropriate",
            "yogurt": "Lactose-free yogurt or a suitable plant-based yogurt",
            "curd": "Lactose-free curd or a suitable plant-based yogurt",
            "ice cream": "Lactose-free or dairy-free frozen dessert",
            "paneer": "Lactose-free paneer or a suitable plant-based alternative",
            "cottage cheese": "Lactose-free cottage cheese where available",
            "cream": "A suitable lactose-free or plant-based cream",
            "milkshake": "A lactose-free or plant-based milkshake",
            "milk chocolate": "A suitable dairy-free chocolate"
        }
    }
]


# =============================================================
# CREATE DATABASE TABLES
# =============================================================

Base.metadata.create_all(bind=engine)


# =============================================================
# INSERT / UPDATE HEALTH RULES
# =============================================================

db = SessionLocal()

try:

    for rule in RULES:

        existing_rule = (
            db.query(HealthRule)
            .filter(
                HealthRule.condition_id == rule["condition_id"]
            )
            .first()
        )

        if existing_rule:

            existing_rule.condition_name = (
                rule["condition_name"]
            )

            existing_rule.high_risk_ingredients = json.dumps(
                rule["high_risk_ingredients"]
            )

            existing_rule.warning = (
                rule["warning"]
            )

            existing_rule.substitutions = json.dumps(
                rule["substitutions"]
            )

        else:

            new_rule = HealthRule(
                condition_id=rule["condition_id"],

                condition_name=rule["condition_name"],

                high_risk_ingredients=json.dumps(
                    rule["high_risk_ingredients"]
                ),

                warning=rule["warning"],

                substitutions=json.dumps(
                    rule["substitutions"]
                )
            )

            db.add(new_rule)

    db.commit()

    print("Health rules updated successfully.")

    print(
        f"Loaded {len(RULES)} health conditions."
    )

    for rule in RULES:
        print(
            f"{rule['condition_name']}: "
            f"{len(rule['high_risk_ingredients'])} risk terms"
        )

finally:

    db.close()