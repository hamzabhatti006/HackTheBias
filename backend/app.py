from flask import Flask, request, jsonify
from flask_cors import CORS
import math

# Import backend logic
from credentials.signup import signup_user
from credentials.verify_email import verify_email
from credentials.login import login_user

app = Flask(__name__)
CORS(app)  # Allow frontend to call backend (important)

# ---------- HEALTH CHECK ----------
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "SilentSpeak backend running"}), 200


# ---------- SIGN UP ----------
@app.route("/signup", methods=["POST"])
def signup():
    payload = request.get_json()

    if not payload:
        return jsonify({
            "success": False,
            "message": "Invalid JSON payload"
        }), 400

    result = signup_user(payload)
    return jsonify(result), 200


# ---------- VERIFY EMAIL ----------
@app.route("/verify-email", methods=["POST"])
def verify():
    payload = request.get_json()

    if not payload:
        return jsonify({
            "verified": False
        }), 400

    result = verify_email(payload)
    return jsonify(result), 200


# ---------- LOGIN ----------
@app.route("/login", methods=["POST"])
def login():
    payload = request.get_json()

    if not payload:
        return jsonify({
            "login": False
        }), 400

    result = login_user(payload)
    return jsonify(result), 200


def _distance(point_a, point_b):
    return math.hypot(point_a["x"] - point_b["x"], point_a["y"] - point_b["y"])


def _finger_extended(landmarks, tip_idx, pip_idx, palm_size):
    return (landmarks[pip_idx]["y"] - landmarks[tip_idx]["y"]) > (0.15 * palm_size)


def _classify_sign(landmarks):
    wrist = landmarks[0]
    index_mcp = landmarks[5]
    palm_size = max(_distance(wrist, index_mcp), 0.05)

    fingers_extended = [
        _finger_extended(landmarks, 8, 6, palm_size),
        _finger_extended(landmarks, 12, 10, palm_size),
        _finger_extended(landmarks, 16, 14, palm_size),
        _finger_extended(landmarks, 20, 18, palm_size),
    ]

    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    thumb_out = _distance(thumb_tip, index_mcp) > (0.7 * palm_size)
    thumb_tucked = thumb_tip["y"] > (thumb_ip["y"] - 0.02)
    thumb_index_dist = _distance(thumb_tip, landmarks[8])

    extended_count = sum(1 for extended in fingers_extended if extended)
    curled_count = 4 - extended_count

    score_a = (curled_count / 4) * 0.7 + (0.3 if thumb_out else 0)
    score_b = (extended_count / 4) * 0.7 + (0.3 if thumb_tucked else 0)
    score_c = 0

    if extended_count >= 3 and thumb_out:
        if 0.25 * palm_size <= thumb_index_dist <= 0.8 * palm_size:
            score_c = 0.6 + (0.2 if curled_count <= 1 else 0) + (0.2 if not thumb_tucked else 0)

    scores = {
        "A": round(score_a, 2),
        "B": round(score_b, 2),
        "C": round(score_c, 2),
    }

    best_label = max(scores, key=scores.get)
    best_score = scores[best_label]

    if best_score < 0.55:
        return {
            "label": "Unknown",
            "confidence": round(best_score, 2),
        }

    return {
        "label": best_label,
        "confidence": best_score,
    }


@app.route("/asl/check", methods=["POST"])
def asl_check():
    payload = request.get_json()

    if not payload:
        return jsonify({
            "success": False,
            "message": "Invalid JSON payload"
        }), 400

    landmarks = payload.get("landmarks")
    target = payload.get("target")

    if not landmarks or not target:
        return jsonify({
            "success": False,
            "message": "Missing landmarks or target sign"
        }), 400

    target = str(target).upper()

    if len(landmarks) < 21:
        return jsonify({
            "success": False,
            "message": "Not enough hand landmarks provided"
        }), 400

    result = _classify_sign(landmarks)
    match = result["label"] == target

    return jsonify({
        "success": True,
        "target": target,
        "prediction": result["label"],
        "confidence": result["confidence"],
        "match": match
    }), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
