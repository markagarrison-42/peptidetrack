from flask import Blueprint, request, jsonify
from flask_login import login_required
import requests
import json
import os

learn_bp = Blueprint("learn", __name__)

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


def claude_request(system, user_msg):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""),
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1000,
        "system": system,
        "messages": [{"role": "user", "content": user_msg}],
    }
    resp = requests.post(ANTHROPIC_API_URL, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


@learn_bp.route("/peptide", methods=["POST"])
@login_required
def peptide_info():
    data = request.get_json()
    name = data.get("name", "")
    if not name:
        return jsonify({"error": "No peptide name provided"}), 400
    try:
        result = claude_request(
            system="You are a peptide reference assistant. Return ONLY valid JSON, no markdown, no explanation. The JSON must have these exact keys: mechanism (2-3 sentences), uses (array of 4-6 strings), dosing (string), frequency (string), route (string), reconstitution (string or null), halfLife (string), sideEffects (array of 3-5 strings), stacks (array of 2-4 strings).",
            user_msg="Provide reference data for the peptide: " + name,
        )
        text = ""
        for block in result.get("content", []):
            if block.get("type") == "text":
                text += block.get("text", "")
        clean = text.replace("```json", "").replace("```", "").strip()
        info = json.loads(clean)
        return jsonify(info), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@learn_bp.route("/research", methods=["GET"])
@login_required
def research():
    try:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""),
            "anthropic-version": "2023-06-01",
        }
        payload = {
            "model": "claude-sonnet-4-6",
            "max_tokens": 2000,
            "tools": [{"type": "web_search_20250305", "name": "web_search"}],
            "system": "You are a research assistant specializing in peptide therapy. After searching the web, you MUST return ONLY a valid JSON array — no prose, no markdown, no explanation. The array must contain up to 8 objects each with exactly these keys: title (string), summary (2-3 sentence string), source (string), date (string), category (one of: Clinical, Research, News, Safety).",
            "messages": [{"role": "user", "content": "Search for the latest peptide therapy research, clinical studies, and news from the past 3 months. Then return your findings as a JSON array."}],
        }
        resp = requests.post(ANTHROPIC_API_URL, json=payload, headers=headers, timeout=45)
        resp.raise_for_status()
        result = resp.json()

        # Collect all text blocks
        text = ""
        for block in result.get("content", []):
            if block.get("type") == "text":
                text += block.get("text", "")

        clean = text.replace("```json", "").replace("```", "").strip()

        # Find the JSON array in the text
        start = clean.find("[")
        end   = clean.rfind("]") + 1
        if start == -1 or end == 0:
            return jsonify({"error": "No JSON array found in response"}), 500

        items = json.loads(clean[start:end])
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
