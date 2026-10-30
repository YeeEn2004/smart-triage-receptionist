# llm_extraction.py
# Your OpenAI symptom-extraction step + a wrapper that turns the result into a zone.
#
# Needs next to it:  system_prompt.py (FINAL_PROMPT)  and  triage_rules.py (evaluate_triage_level)
# Needs installed:   pip install openai
# Needs set:         OPENAI_API_KEY environment variable

import json
import os
import re

import streamlit as st
from openai import OpenAI

from system_prompt import FINAL_PROMPT
from triage_rules import evaluate_triage_level

_client = None


def _get_client() -> OpenAI:
    """Create the API client on first use, so the app still opens if the key is missing."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _client


def get_llm_extraction(patient_text: str) -> list:
    """
    Sends the patient's text to the LLM Cloud API and returns the extracted symptoms.
    Returns [] if the call fails.
    """
    try:
        response = _get_client().chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},  # Forces strict JSON output
            messages=[
                {"role": "system", "content": FINAL_PROMPT},
                {"role": "user", "content": patient_text},
            ],
            temperature=0.0,  # Deterministic extraction
        )
        result = json.loads(response.choices[0].message.content)
        return result.get("extracted_symptoms", [])

    except Exception as e:
        st.error(f"API Connection Error: {e}")
        return []


# ------------------------------------------------------------------
# Turn whatever evaluate_triage_level() returns into "red" / "amber" / "green"
# ------------------------------------------------------------------
_ZONE_KEYS = ("zone", "triage_zone", "level", "triage_level", "category", "colour", "color", "result")


def _zone_from_text(text: str):
    text = text.lower()
    if re.search(r"\b(red|merah|resus\w*|critical)\b", text) and "semi" not in text:
        return "red"
    if re.search(r"\b(yellow|amber|kuning|urgent|semi\W?critical)\b", text):
        return "amber"
    if re.search(r"\b(green|hijau|non\W?critical|outpatient)\b", text):
        return "green"
    return None


def _normalise_zone(result):
    if isinstance(result, str):
        return _zone_from_text(result)
    if isinstance(result, dict):
        for key in _ZONE_KEYS:
            if key in result and isinstance(result[key], str):
                zone = _zone_from_text(result[key])
                if zone:
                    return zone
        return None
    if isinstance(result, (list, tuple)) and result:
        return _normalise_zone(result[0])
    return None


def classify(patient_text: str):
    """
    patient_text is the structured string built by the UI (Age / Gender / History / Symptoms).
    Returns (zone, symptoms) where zone is "red", "amber", "green" or None
    (None means the AI step could not decide, so the caller should fall back).
    """
    symptoms = get_llm_extraction(patient_text)
    if not symptoms:
        return None, []
    try:
        zone = _normalise_zone(evaluate_triage_level(symptoms))
    except Exception as e:
        st.error(f"Triage rules error: {e}")
        zone = None
    return zone, symptoms