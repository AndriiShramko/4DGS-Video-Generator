"""Central registry for the local video-editing models.

Single source of truth for HuggingFace repo ids, upstream git repos, local paths
and per-model defaults. Backends in ``backends/`` read from here so that updating
a weight id or clone URL is a one-line change.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# Resolve everything relative to this file so the tool works from any cwd.
ROOT = Path(__file__).resolve().parent
VENDOR_DIR = ROOT / "vendor"     # upstream model repos cloned by install.sh
WEIGHTS_DIR = ROOT / "weights"   # downloaded checkpoints (gitignored)
OUTPUT_DIR = ROOT / "outputs"

# Allow overriding the weights cache (e.g. point at a big scratch disk).
WEIGHTS_DIR = Path(os.environ.get("VIDEO_EDIT_WEIGHTS", WEIGHTS_DIR))


@dataclass(frozen=True)
class ModelSpec:
    key: str                 # CLI selector, e.g. "kiwi"
    name: str                # human name
    hf_repo: str             # HuggingFace weights repo id
    git_repo: str            # upstream code repo (cloned into vendor/)
    backend: str             # module name in backends/ that drives it
    license: str             # short license tag
    commercial_ok: bool      # may be used commercially
    default_frames: int = 81
    default_size: tuple[int, int] = (480, 832)  # (height, width)
    notes: str = ""
    extras: dict = field(default_factory=dict)

    @property
    def vendor_path(self) -> Path:
        return VENDOR_DIR / self.key

    @property
    def weights_path(self) -> Path:
        return WEIGHTS_DIR / self.key


# --- Model registry -------------------------------------------------------

MODELS: dict[str, ModelSpec] = {
    "kiwi": ModelSpec(
        key="kiwi",
        name="Kiwi-Edit",
        hf_repo="linyq/kiwi-edit-5b-instruct-only-diffusers",
        git_repo="https://github.com/showlab/Kiwi-Edit",
        backend="kiwi_edit",
        license="MIT",
        commercial_ok=True,
        notes="Best evidence-backed open editor (OpenVE-Bench #1). Default pick.",
        extras={
            # Reference-guided variant used when --reference is supplied.
            "hf_repo_reference": "linyq/kiwi-edit-5b-instruct-reference-diffusers",
        },
    ),
    "live": ModelSpec(
        key="live",
        name="LIVEditor-14B",
        hf_repo="sst12345/liveditor",
        git_repo="https://github.com/xie-lab-ml/Lightning-Unified-Video-Editor-via-In-Context-Sparse-Attention",
        backend="liveditor",
        license="unstated-verify",
        commercial_ok=False,
        default_size=(480, 832),
        notes="14B; triple-benchmark winner claim. Single-GPU on 96 GB. Verify license.",
    ),
    "ditto": ModelSpec(
        key="ditto",
        name="Ditto/Editto",
        hf_repo="QingyanBai/Ditto_models",
        git_repo="https://github.com/EzioBy/Ditto",
        backend="ditto",
        license="CC-BY-NC-SA-4.0",
        commercial_ok=False,
        notes="IVEBench instruction-following leader. Research only.",
    ),
    "lucy": ModelSpec(
        key="lucy",
        name="Lucy-Edit-Dev",
        hf_repo="decart-ai/Lucy-Edit-1.1-Dev",
        git_repo="https://github.com/DecartAI/diffusers-lucy-edit",
        backend="lucy_edit",
        license="Non-Commercial",
        commercial_ok=False,
        notes="Fast 5B, clean LucyEditPipeline. Quick localized edits.",
    ),
    # Post-processing upscaler (not an editor; invoked via --upscale).
    "seedvr2": ModelSpec(
        key="seedvr2",
        name="SeedVR2-7B",
        hf_repo="ByteDance-Seed/SeedVR2-7B",
        git_repo="https://github.com/ByteDance-Seed/SeedVR",
        backend="seedvr2",
        license="research",
        commercial_ok=False,
        notes="Temporally-consistent video upscaler used by --upscale.",
    ),
}

# Editors that can be selected with --model / --compare-all (excludes the upscaler).
EDITORS = [k for k, m in MODELS.items() if m.key != "seedvr2"]

DEFAULT_MODEL = "kiwi"
UPSCALER = "seedvr2"


def get(key: str) -> ModelSpec:
    if key not in MODELS:
        raise KeyError(
            f"Unknown model '{key}'. Available: {', '.join(MODELS)}"
        )
    return MODELS[key]
