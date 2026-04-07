"""
app.py — Flask API untuk FinBERT Sentiment Analysis
======================================================
Endpoints:
  GET  /health          → status server & model
  GET  /model-info      → info model yang sedang dipakai
  POST /predict         → prediksi single teks
  POST /predict/batch   → prediksi banyak teks sekaligus
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional

import torch
import torch.nn.functional as F
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ─── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ─── Konfigurasi ───────────────────────────────────────────────────────────────
# Urutan prioritas: sistem akan mencoba path satu per satu
MODEL_CANDIDATES = [
    "./best_finbert_model",
    "./finbert_results/checkpoint-726",
    "./finbert_results/checkpoint-484",
]

# Label sesuai urutan id2label di config.json model kamu
# 0=negative, 1=neutral, 2=positive  ← sesuaikan jika berbeda
LABEL_MAP = {0: "negative", 1: "neutral", 2: "positive"}

MAX_LENGTH  = 512   # max token per input
MAX_BATCH   = 20    # batas maksimal teks dalam satu batch request

# ─── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # izinkan semua origin (dev)

# ─── State global model ────────────────────────────────────────────────────────
tokenizer:    Optional[AutoTokenizer]                        = None
model:        Optional[AutoModelForSequenceClassification]   = None
device:       torch.device                                   = torch.device("cpu")
model_path:   str                                            = ""
load_time:    float                                          = 0.0

# ─── Fungsi cari & load model ──────────────────────────────────────────────────
def find_model_path() -> str:
    """
    Cari model pertama yang valid dari MODEL_CANDIDATES.
    Valid = folder ada DAN berisi file bobot model.
    """
    weight_files = {"model.safetensors", "pytorch_model.bin"}

    for candidate in MODEL_CANDIDATES:
        p = Path(candidate)
        if not p.exists():
            log.warning(f"  Tidak ditemukan: {candidate}")
            continue

        found_weights = any((p / f).exists() for f in weight_files)
        if not found_weights:
            log.warning(f"  Folder ada tapi tidak ada bobot model di: {candidate}")
            log.warning(f"  (tidak ada {weight_files})")
            continue

        log.info(f"  Model ditemukan di: {candidate}")
        return candidate

    # Tidak ada yang valid — tampilkan petunjuk dan keluar
    log.error("=" * 60)
    log.error("GAGAL: Tidak ada model yang valid ditemukan!")
    log.error("Pastikan salah satu path berikut berisi model weights:")
    for c in MODEL_CANDIDATES:
        log.error(f"  -> {c}")
    log.error("")
    log.error("Solusi: Jalankan dahulu script berikut untuk export model:")
    log.error("  python save_best_model.py")
    log.error("=" * 60)
    sys.exit(1)


def load_model():
    """Load tokenizer + model ke device yang tersedia."""
    global tokenizer, model, device, model_path, load_time

    model_path = find_model_path()

    # Pilih device
    if torch.cuda.is_available():
        device = torch.device("cuda")
        log.info(f"GPU tersedia: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        log.info("GPU tidak tersedia, menggunakan CPU")

    log.info(f"Loading model dari: {model_path}")
    t0 = time.time()

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        model.to(device)
        model.eval()
        load_time = round(time.time() - t0, 2)
        log.info(f"Model berhasil dimuat dalam {load_time}s di {device}")

    except Exception as e:
        log.error(f"Gagal load model: {e}")
        sys.exit(1)


# ─── Fungsi prediksi ───────────────────────────────────────────────────────────
def predict_single(text: str) -> dict:
    """Prediksi sentimen untuk satu teks."""
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_LENGTH,
        padding=True,
    ).to(device)

    with torch.no_grad():
        logits = model(**inputs).logits
        probs  = F.softmax(logits, dim=-1).squeeze().tolist()

        # Handle edge case jika hanya 1 sampel (squeeze terlalu agresif)
        if isinstance(probs, float):
            probs = [probs]

    pred_idx = int(torch.argmax(logits, dim=-1).item())
    label    = LABEL_MAP.get(pred_idx, "unknown")

    return {
        "label":       label,
        "confidence":  round(probs[pred_idx], 6),
        "probabilities": {
            LABEL_MAP[i]: round(p, 6)
            for i, p in enumerate(probs)
            if i in LABEL_MAP
        },
    }


def validate_text(text) -> tuple:
    """
    Validasi input teks.
    Return: (cleaned_text, error_message)
    """
    if not isinstance(text, str):
        return None, "Teks harus berupa string"
    text = text.strip()
    if not text:
        return None, "Teks tidak boleh kosong"
    if len(text) > 10_000:
        return None, "Teks terlalu panjang (maksimal 10.000 karakter)"
    return text, None


# ─── Endpoints ─────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    """Cek status server dan model."""
    return jsonify({
        "status":       "ok",
        "model_loaded": model is not None,
        "device":       str(device),
        "model_path":   model_path,
        "load_time_s":  load_time,
    })


@app.route("/model-info", methods=["GET"])
def model_info():
    """Info detail model yang sedang berjalan."""
    if model is None:
        return jsonify({"error": "Model belum dimuat"}), 503

    num_labels = model.config.num_labels
    return jsonify({
        "model_path":   model_path,
        "num_labels":   num_labels,
        "label_map":    LABEL_MAP,
        "device":       str(device),
        "max_length":   MAX_LENGTH,
        "architecture": model.config.model_type,
        "load_time_s":  load_time,
    })


@app.route("/predict", methods=["POST"])
def predict():
    """
    Prediksi sentimen satu teks.

    Request body (JSON):
      { "text": "string" }

    Response:
      {
        "label": "positive" | "neutral" | "negative",
        "confidence": 0.98,
        "probabilities": { "positive": 0.98, "neutral": 0.01, "negative": 0.01 },
        "inference_ms": 42.3
      }
    """
    if model is None:
        return jsonify({"error": "Model belum siap"}), 503

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body harus JSON"}), 400

    text, err = validate_text(data.get("text"))
    if err:
        return jsonify({"error": err}), 400

    try:
        t0     = time.time()
        result = predict_single(text)
        result["inference_ms"] = round((time.time() - t0) * 1000, 1)
        return jsonify(result)

    except Exception as e:
        log.error(f"Error saat prediksi: {e}", exc_info=True)
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@app.route("/predict/batch", methods=["POST"])
def predict_batch():
    """
    Prediksi sentimen banyak teks sekaligus.

    Request body (JSON):
      { "texts": ["teks1", "teks2", ...] }

    Response:
      {
        "results": [
          {
            "index": 0,
            "text_preview": "...",
            "label": "positive",
            "confidence": 0.9,
            "probabilities": { ... }
          },
          ...
        ],
        "summary": {
          "positive": 1, "neutral": 1, "negative": 0,
          "total": 2, "errors": 0
        }
      }
    """
    if model is None:
        return jsonify({"error": "Model belum siap"}), 503

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body harus JSON"}), 400

    texts = data.get("texts")
    if not isinstance(texts, list) or len(texts) == 0:
        return jsonify({"error": "Field 'texts' harus berupa array tidak kosong"}), 400
    if len(texts) > MAX_BATCH:
        return jsonify({"error": f"Maksimal {MAX_BATCH} teks per request"}), 400

    results = []
    summary = {v: 0 for v in LABEL_MAP.values()}
    summary["total"]  = 0
    summary["errors"] = 0

    for i, raw_text in enumerate(texts):
        text, err = validate_text(raw_text)
        if err:
            results.append({"index": i, "error": err})
            summary["errors"] += 1
            continue

        try:
            pred = predict_single(text)
            results.append({
                "index":        i,
                "text_preview": text[:80] + ("..." if len(text) > 80 else ""),
                **pred,
            })
            summary[pred["label"]] = summary.get(pred["label"], 0) + 1
            summary["total"] += 1

        except Exception as e:
            log.error(f"Error pada teks index {i}: {e}", exc_info=True)
            results.append({"index": i, "error": str(e)})
            summary["errors"] += 1

    return jsonify({"results": results, "summary": summary})


# ─── Error handlers global ─────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint tidak ditemukan"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method tidak diizinkan"}), 405

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ─── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("=" * 50)
    log.info("  FinBERT Sentiment Analysis API")
    log.info("=" * 50)
    load_model()
    log.info("Server berjalan di http://localhost:5000")
    log.info("Endpoints tersedia:")
    log.info("  GET  /health")
    log.info("  GET  /model-info")
    log.info("  POST /predict")
    log.info("  POST /predict/batch")
    log.info("=" * 50)
    app.run(
        debug=False,   # set True hanya saat development
        host="0.0.0.0",
        port=5000,
    )