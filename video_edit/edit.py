#!/usr/bin/env python3
"""Unified CLI for local prompt-based video-to-video editing.

No ComfyUI, no nodes — one command drives any of the bundled models and
(optionally) the SeedVR2 upscaler.

Examples
--------
    # Default MIT model (Kiwi-Edit)
    python edit.py --model kiwi --input in.mp4 --prompt "make it a snowy night" --output out.mp4

    # 14B model, flexing the 96 GB card, then upscale to ~4K
    python edit.py --model live --input in.mp4 --prompt "cyberpunk neon city" \
        --output out.mp4 --upscale

    # Reference-guided edit
    python edit.py --model kiwi --input in.mp4 --prompt "wear this jacket" \
        --reference jacket.png --output out.mp4

    # Compare every editor on the same clip
    python edit.py --compare-all --input in.mp4 --prompt "make it autumn" --output compare/
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import config
import backends


def build_request(args, model_key: str, output: Path) -> backends.EditRequest:
    spec = config.get(model_key)
    h, w = spec.default_size
    return backends.EditRequest(
        input=Path(args.input),
        prompt=args.prompt,
        output=output,
        reference=Path(args.reference) if args.reference else None,
        frames=args.frames or spec.default_frames,
        height=args.height or h,
        width=args.width or w,
        steps=args.steps,
        seed=args.seed,
        fps=args.fps,
        dtype=args.dtype,
        enhance_prompt=args.enhance_prompt,
    )


def run_one(model_key: str, req: backends.EditRequest, do_upscale: bool,
            scale: int) -> Path:
    spec = config.get(model_key)
    if not spec.commercial_ok:
        print(f"  note: {spec.name} license = {spec.license} (non-commercial).")

    backend = backends.load(model_key)
    t0 = time.time()
    print(f"==> [{spec.name}] editing -> {req.output}")
    edited = backend.run(req)
    print(f"    edit done in {time.time() - t0:.1f}s")

    if do_upscale:
        up = backends.load(config.UPSCALER)
        out_up = edited.with_name(edited.stem + "_4k" + edited.suffix)
        print(f"==> [SeedVR2] upscaling x{scale} -> {out_up}")
        t1 = time.time()
        edited = up.upscale(edited, out_up, scale=scale, seed=req.seed)  # type: ignore[attr-defined]
        print(f"    upscale done in {time.time() - t1:.1f}s")
    return edited


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        description="Local prompt-based video-to-video editing (RTX PRO 6000).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--model", choices=config.EDITORS, default=config.DEFAULT_MODEL,
                   help="which editor to use")
    p.add_argument("--compare-all", action="store_true",
                   help="run every editor on the same clip; --output is a directory")
    p.add_argument("--input", required=True, help="source video (mp4)")
    p.add_argument("--prompt", required=True, help="edit instruction")
    p.add_argument("--output", required=True, help="output mp4 (or dir for --compare-all)")
    p.add_argument("--reference", help="optional reference image for reference-guided edits")

    p.add_argument("--upscale", action="store_true", help="post-process with SeedVR2")
    p.add_argument("--scale", type=int, default=2, help="upscale factor for SeedVR2")

    p.add_argument("--frames", type=int, default=0, help="frames per window (0 = model default)")
    p.add_argument("--height", type=int, default=0, help="override height (0 = model default)")
    p.add_argument("--width", type=int, default=0, help="override width (0 = model default)")
    p.add_argument("--steps", type=int, default=30, help="sampler steps")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--fps", type=int, default=None, help="output fps (default: keep source)")
    p.add_argument("--dtype", choices=["bf16", "fp16", "fp32"], default="bf16",
                   help="precision; 96 GB can afford fp32")
    p.add_argument("--enhance-prompt", action="store_true",
                   help="use an upstream LLM prompt-enhancer if the backend supports it")

    args = p.parse_args(argv)

    if not Path(args.input).exists():
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 2

    if args.compare_all:
        out_dir = Path(args.output)
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"Comparing {len(config.EDITORS)} models -> {out_dir}\n")
        for key in config.EDITORS:
            out = out_dir / f"{key}.mp4"
            try:
                req = build_request(args, key, out)
                run_one(key, req, args.upscale, args.scale)
            except Exception as exc:  # noqa: BLE001 - keep comparing other models
                print(f"    {key} FAILED: {exc}\n", file=sys.stderr)
        print("\nComparison done.")
        return 0

    out = Path(args.output)
    req = build_request(args, args.model, out)
    final = run_one(args.model, req, args.upscale, args.scale)
    print(f"\nDone -> {final}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
