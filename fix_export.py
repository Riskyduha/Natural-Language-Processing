import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

CHECKPOINT = "./finbert_results/checkpoint-726"
SAVE_TO    = "./best_finbert_model"
BASE_MODEL = "ProsusAI/finbert"

print("=" * 50)
print("  Fix Export Model")
print("=" * 50)

# 1. Cek isi checkpoint
print(f"\nIsi folder {CHECKPOINT}:")
for f in sorted(os.listdir(CHECKPOINT)):
    size = os.path.getsize(os.path.join(CHECKPOINT, f)) // 1024
    print(f"  {f:<40} {size:>8} KB")

# 2. Load tokenizer dari base model (tidak butuh file bobot)
print(f"\nLoading tokenizer dari base model: {BASE_MODEL}")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
print("  OK")

# 3. Load model dari checkpoint dengan rename LayerNorm
#    (fix: gamma/beta → weight/bias yang menyebabkan missing keys)
print(f"\nLoading model dari checkpoint: {CHECKPOINT}")

# Load state dict manual dari checkpoint
import glob

# Cari file state dict di checkpoint
state_dict_files = (
    glob.glob(os.path.join(CHECKPOINT, "*.safetensors")) +
    glob.glob(os.path.join(CHECKPOINT, "pytorch_model*.bin")) +
    glob.glob(os.path.join(CHECKPOINT, "model*.safetensors"))
)

print(f"  File state dict ditemukan: {state_dict_files}")

if state_dict_files:
    # Ada file bobot langsung
    model = AutoModelForSequenceClassification.from_pretrained(
        CHECKPOINT,
        num_labels=3,
        id2label={0: "negative", 1: "neutral", 2: "positive"},
        label2id={"negative": 0, "neutral": 1, "positive": 2},
        ignore_mismatched_sizes=True,
    )
else:
    # Tidak ada file bobot di checkpoint — load dari base lalu patch dengan state dict trainer
    print("  Tidak ada file bobot di checkpoint, coba load via trainer state...")

    # Cek apakah ada optimizer.pt (tandanya checkpoint trainer)
    optimizer_file = os.path.join(CHECKPOINT, "optimizer.pt")
    if not os.path.exists(optimizer_file):
        print(f"  ERROR: {optimizer_file} tidak ada!")
        print("  Checkpoint tidak valid, coba checkpoint lain.")
        exit(1)

    # Load base model lalu load bobot dari training via Trainer
    from transformers import TrainingArguments, Trainer
    from datasets import Dataset
    import numpy as np

    print("  Loading base model...")
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=3,
        id2label={0: "negative", 1: "neutral", 2: "positive"},
        label2id={"negative": 0, "neutral": 1, "positive": 2},
        ignore_mismatched_sizes=True,
    )

    # Resume dari checkpoint
    print(f"  Resume weights dari checkpoint...")
    from transformers.modeling_utils import load_sharded_checkpoint
    
    # Coba load model_state langsung via torch
    # Checkpoint Trainer menyimpan bobot di model.safetensors ATAU terpisah per shard
    # Kalau tidak ada, berarti trainer pakai format lama (pytorch_model.bin di folder induk)
    
    # Cek folder finbert_results langsung
    results_dir = "./finbert_results"
    alt_files = (
        glob.glob(os.path.join(results_dir, "*.safetensors")) +
        glob.glob(os.path.join(results_dir, "pytorch_model*.bin"))
    )
    
    if alt_files:
        print(f"  Ditemukan di {results_dir}: {alt_files}")
        state_dict = torch.load(alt_files[0], map_location="cpu")
        
        # Rename gamma/beta → weight/bias (fix LayerNorm naming)
        new_state_dict = {}
        for k, v in state_dict.items():
            k = k.replace(".gamma", ".weight").replace(".beta", ".bias")
            new_state_dict[k] = v
        
        missing, unexpected = model.load_state_dict(new_state_dict, strict=False)
        print(f"  Missing keys : {len(missing)}")
        print(f"  Unexpected   : {len(unexpected)}")
    else:
        print("\n  TIDAK DITEMUKAN file bobot di manapun!")
        print("  Solusi: Jalankan main.py ulang atau jalankan cell export di notebook")
        exit(1)

print("  Model berhasil dimuat!")
print(f"  Arsitektur : {model.config.model_type}")
print(f"  Num labels : {model.config.num_labels}")
print(f"  Label map  : {model.config.id2label}")

# 4. Simpan
print(f"\nMenyimpan ke: {SAVE_TO}")
os.makedirs(SAVE_TO, exist_ok=True)
model.save_pretrained(SAVE_TO)
tokenizer.save_pretrained(SAVE_TO)

# 5. Verifikasi
print("\nFile tersimpan:")
for f in sorted(os.listdir(SAVE_TO)):
    size = os.path.getsize(os.path.join(SAVE_TO, f)) // 1024
    print(f"  {f:<40} {size:>8} KB")

has_weights = any(
    f in ("model.safetensors", "pytorch_model.bin")
    for f in os.listdir(SAVE_TO)
)

print("\n" + "=" * 50)
if has_weights:
    print("  BERHASIL! Sekarang jalankan: python app.py")
else:
    print("  GAGAL: File bobot tidak tersimpan!")
print("=" * 50)