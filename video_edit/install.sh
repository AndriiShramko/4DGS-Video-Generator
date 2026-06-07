#!/usr/bin/env bash
#
# Environment setup for local prompt-based video editing on
# NVIDIA RTX PRO 6000 Blackwell (96 GB, compute capability sm_120).
#
# Creates ./venv, installs a Blackwell-compatible PyTorch nightly + deps,
# builds SageAttention, and clones the upstream model repos into ./vendor.
#
# Usage:  bash install.sh
# After:  source venv/bin/activate && python download_models.py
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

# Pin a CUDA build that ships sm_120 kernels. cu128 nightlies are the first to
# support Blackwell; stable cu121/cu124 wheels fail with "no kernel image".
TORCH_INDEX="https://download.pytorch.org/whl/nightly/cu128"
PYTHON="${PYTHON:-python3.11}"

echo "==> [1/6] Creating virtual environment (venv) with $PYTHON"
"$PYTHON" -m venv venv
# shellcheck disable=SC1091
source venv/bin/activate
python -m pip install --upgrade pip wheel setuptools

echo "==> [2/6] Installing PyTorch nightly (cu128 / sm_120) for Blackwell"
# If a newer stable build already supports sm_120, you may switch TORCH_INDEX to
# the stable cu128 channel. Verify with: python -c "import torch;print(torch.cuda.get_arch_list())"
pip install --pre torch torchvision torchaudio --index-url "$TORCH_INDEX"

echo "==> [3/6] Installing Python dependencies"
pip install -r requirements.txt

echo "==> [4/6] Installing SageAttention 2.2 (Blackwell attention accelerator)"
# Prefer a prebuilt sm_120 wheel matched to this torch/cuda; fall back to source.
# FlashAttention is intentionally skipped (hard to build on Blackwell, and the
# CUDA SageAttention backend avoids the Triton black-frame issue with Wan).
if ! pip install sageattention 2>/dev/null; then
  echo "    prebuilt wheel unavailable -> building SageAttention from source"
  pip install "git+https://github.com/thu-ml/SageAttention.git" || \
    echo "    WARN: SageAttention build failed; models will fall back to SDPA (slower)."
fi

echo "==> [5/6] Cloning upstream model repositories into ./vendor"
mkdir -p vendor
clone() {  # clone <key> <git-url>
  local key="$1" url="$2"
  if [ -d "vendor/$key/.git" ]; then
    echo "    vendor/$key already present -> git pull"
    git -C "vendor/$key" pull --ff-only || true
  else
    echo "    cloning $url -> vendor/$key"
    git clone --depth 1 "$url" "vendor/$key" || \
      echo "    WARN: failed to clone $url (network policy?). Retry later."
  fi
}
clone kiwi    https://github.com/showlab/Kiwi-Edit
clone live    https://github.com/xie-lab-ml/Lightning-Unified-Video-Editor-via-In-Context-Sparse-Attention
clone ditto   https://github.com/EzioBy/Ditto
clone lucy    https://github.com/DecartAI/diffusers-lucy-edit
clone seedvr2 https://github.com/ByteDance-Seed/SeedVR

# Install per-repo python requirements if present (best-effort).
for d in vendor/*/; do
  if [ -f "${d}requirements.txt" ]; then
    echo "    installing requirements for ${d}"
    pip install -r "${d}requirements.txt" || \
      echo "    WARN: some deps in ${d}requirements.txt failed; review manually."
  fi
done

echo "==> [6/6] Environment summary"
python - <<'PY'
import torch
print("  torch       :", torch.__version__)
print("  cuda avail  :", torch.cuda.is_available())
if torch.cuda.is_available():
    print("  device      :", torch.cuda.get_device_name(0))
    print("  arch list   :", torch.cuda.get_arch_list())
    free, total = torch.cuda.mem_get_info()
    print(f"  VRAM        : {total/1e9:.0f} GB total")
    if "sm_120" not in "".join(torch.cuda.get_arch_list()):
        print("  WARNING: this torch build has no sm_120 kernels -> Blackwell will fail.")
PY

echo
echo "Done. Next:"
echo "  source venv/bin/activate"
echo "  python download_models.py        # fetch model weights"
echo "  python edit.py --help"
