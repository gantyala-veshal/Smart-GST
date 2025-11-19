# app.py
import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from backend.gst_engine import gst_calculation
from backend.history_manager import read_history
from backend.fraud_detector import check_fraud
from backend.pdfgenerator import generate_invoice

app = Flask(__name__, static_folder="static", template_folder="templates")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json() or {}
    product = data.get("product", "").strip()
    price_raw = data.get("price", "")
    # read optional flags (defaults)
    gst_type = data.get("gst_type", "exclusive")       # "exclusive" or "inclusive"
    gst_category = data.get("gst_category", "cgst_sgst")  # "cgst_sgst" or "igst"

    try:
        price = float(price_raw)
    except Exception:
        return jsonify({"error": "Invalid price"}), 400

    if not product or price <= 0:
        return jsonify({"error": "Invalid input"}), 400

    # pass gst_type and gst_category into calculation
    try:
        rate, gst_amount, total, category = gst_calculation(
            product, price, gst_type=gst_type, gst_category=gst_category
        )
    except Exception as e:
        return jsonify({"error": "Calculation failed", "detail": str(e)}), 500

    return jsonify({
        "rate": rate,
        "gst": gst_amount,
        "total": total,
        "category": category
    })


@app.route("/history", methods=["GET"])
def history():
    rows = read_history()
    return jsonify(rows)


@app.route("/api/check_fraud", methods=["POST"])
def api_check_fraud():
    data = request.get_json() or {}
    try:
        final = float(data.get("final", 0))
        billed = float(data.get("billed", 0))
    except Exception:
        return jsonify({"error": "Invalid numbers"}), 400

    result = check_fraud(final, billed)
    return jsonify({"result": result})


@app.route("/api/generate_invoice", methods=["POST"])
def api_generate_invoice():
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        filename = generate_invoice(text)
    except Exception as e:
        return jsonify({"error": "Failed to generate PDF", "detail": str(e)}), 500

    if not os.path.exists(filename):
        return jsonify({"error": "PDF not found"}), 500

    directory, fname = os.path.split(os.path.abspath(filename))
    return send_from_directory(directory, fname, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
