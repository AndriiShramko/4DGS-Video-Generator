#!/usr/bin/env python3
"""Download model weights into ./weights via the HuggingFace Hub.

Usage:
    python download_models.py                 # download the default editor (kiwi) + upscaler
    python download_models.py kiwi live       # download specific models
    python download_models.py --all           # download everything (large!)

Set HF_TOKEN in the environment for gated repos. Weights land in
config.WEIGHTS_DIR (override with VIDEO_EDIT_WEIGHTS).
"""
from __future__ import annotations

import argparse
import sys

import config


def download(spec: config.ModelSpec) -> None:
    from huggingface_hub import snapshot_download

    spec.weights_path.mkdir(parents=True, exist_ok=True)
    print(f"==> {spec.name}: downloading {spec.hf_repo}")
    snapshot_download(
        repo_id=spec.hf_repo,
        local_dir=str(spec.weights_path),
        local_dir_use_symlinks=False,
    )
    # Some models (Kiwi-Edit reference variant) ship a second repo.
    ref = spec.extras.get("hf_repo_reference")
    if ref:
        print(f"    + reference weights {ref}")
        snapshot_download(
            repo_id=ref,
            local_dir=str(spec.weights_path / "reference"),
            local_dir_use_symlinks=False,
        )
    print(f"    -> {spec.weights_path}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Download video-editing model weights.")
    parser.add_argument("models", nargs="*", help="model keys (default: kiwi + seedvr2)")
    parser.add_argument("--all", action="store_true", help="download every registered model")
    args = parser.parse_args(argv)

    if args.all:
        keys = list(config.MODELS)
    elif args.models:
        keys = args.models
    else:
        keys = [config.DEFAULT_MODEL, config.UPSCALER]

    print(f"Weights dir: {config.WEIGHTS_DIR}")
    print(f"Downloading: {', '.join(keys)}\n")
    for key in keys:
        try:
            download(config.get(key))
        except Exception as exc:  # noqa: BLE001 - report and continue to next model
            print(f"    ERROR downloading {key}: {exc}", file=sys.stderr)
    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
