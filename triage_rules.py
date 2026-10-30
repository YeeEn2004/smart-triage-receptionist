# triage_rules.py

PRIMARY_TRIAGE_RULES = {
    "RED": {
        "mts_level": "Level 1 - Resuscitation",
        "target_response_time": "0 minutes",
        "designated_route": "Resuscitation Bay",
        "clinical_criteria": [
            "cardiac arrest",
            "not breathing",
            "major trauma in shock",
            "severe respiratory distress",
            "not responding to call",
            "severe chest pain",
            "severe pain",
            "ongoing seizures",
            "arterial limb bleeding",
            "active uncontrolled bleeding",
            "massive vaginal bleed"
        ] # Extracted directly from MTS Critical First Look and Rapid Assessment
    },
    "YELLOW": {
        "mts_level": "Level 2 - Emergency",
        "target_response_time": "under 10 minutes",
        "designated_route": "Primary Triage Counter",
        "clinical_criteria": [
            "altered mental state",
            "cannot communicate",
            "cannot sit or stand unsupported",
            "difficulty to breath",
            "short phrases only",
            "active vomit or cough blood",
            "suspected vascular injury",
            "confused",
            "lethargic"
        ]
    },
    "GREEN": {
        "mts_level": "Level 3 - Urgent / Secondary Triage Routing",
        "target_response_time": "under 30 minutes",
        "designated_route": "Standard Outpatient Clinic Waiting Area",
        "clinical_criteria": [
            "walking",
            "talking",
            "not distressed",
            "not aggressive",
            "not breathless",
            "minimal or no active bleeding",
            "fully conscious"
        ]
    }
}

def evaluate_triage_level(extracted_symptoms: list) -> str:
    """
    Deterministic rule engine that overrides AI guessing.
    Matches LLM-extracted symptoms against the hardcoded MTS guidelines.
    """
    # 1. Check for any Red Zone (Level 1) triggers
    for symptom in extracted_symptoms:
        if symptom in PRIMARY_TRIAGE_RULES["RED"]["clinical_criteria"]:
            return "RED"
            
    # 2. Check for any Yellow Zone (Level 2) triggers
    for symptom in extracted_symptoms:
        if symptom in PRIMARY_TRIAGE_RULES["YELLOW"]["clinical_criteria"]:
            return "YELLOW"
            
    # 3. Default to Green Zone if no critical triggers are found
    return "GREEN"