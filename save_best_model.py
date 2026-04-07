import os, sys, json, logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)

BASE_PATH = "./finbert_results"
SAVE_PATH = "./best_finbert_model"


def find_best_checkpoint():
    trainer_state_path = Path(BASE_PATH) / "trainer_state.json"

    if not trainer_state_path.exists():
        log.warning("trainer_state.json tidak ditemukan di root, fallback manual")
        return None

    with open(trainer_state_path) as f:
        state = json.load(f)

    best_ckpt = state.get("best_model_checkpoint", None)

    log.info(f"Best metric           : {state.get('best_metric', 'N/A')}")
    log.info(f"Best model checkpoint : {best_ckpt}")

    return best_ckpt


def main():
    log.info("=" * 55)
    log.info("  Export Model dari Checkpoint")
    log.info("=" * 55)

    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
    except ImportError as e:
        log.error(f"Library tidak ditemukan: {e}")
        sys.exit(1)

    # 🔥 Cari best checkpoint otomatis
    checkpoint_path = find_best_checkpoint()

    # 🔥 Fallback kalau checkpoint tidak valid
    if checkpoint_path is None or not Path(checkpoint_path).exists():
        log.warning("Checkpoint terbaik tidak valid, pakai folder final model")
        checkpoint_path = "./best_finbert_model"

    log.info(f"Loading tokenizer dari: {checkpoint_path}")
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)

    log.info(f"Loading model dari: {checkpoint_path}")
    model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path)

    log.info(f"Arsitektur: {model.config.model_type}, Labels: {model.config.num_labels}")

    log.info(f"Menyimpan ke: {SAVE_PATH}")
    os.makedirs(SAVE_PATH, exist_ok=True)

    model.save_pretrained(SAVE_PATH)
    tokenizer.save_pretrained(SAVE_PATH)

    log.info("=" * 55)
    log.info("  BERHASIL! Sekarang jalankan: python app.py")
    log.info("=" * 55)


if __name__ == "__main__":
    main()