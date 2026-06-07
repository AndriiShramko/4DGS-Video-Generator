# Local Prompt-Based Video-to-Video Editing (RTX PRO 6000 Blackwell)

A **node-free, fully scripted** pipeline for editing video by text prompts, running
100% locally on a single NVIDIA **RTX PRO 6000 Blackwell (96 GB)** workstation.

> Edit a clip with one command:
> ```bash
> python edit.py --model kiwi --input clip.mp4 \
>     --prompt "change the jacket to red leather" --output out.mp4 --upscale
> ```

This is **not** ComfyUI. There are no nodes. Every model is driven from Python / CLI.

## Why these models (research, June 2026)

A 3-agent research sweep compared every open prompt-editing model that ships
downloadable weights. The shortlist below survived independent benchmarks
(IVEBench ICLR'26, EditVerseBench, OpenVE-Bench) and a "runs programmatically on
one GPU" filter. Models that lost: **Bernini** (only the renderer is open, every
official video path needs 8 GPUs, zero independent benchmarks) and **Lucy Edit**
(non-commercial license, mid-pack on IVEBench) — Lucy is still bundled here as a
fast lightweight option since this deployment is research/personal use.

| Key  | Model          | Base                     | License        | Why it's here |
|------|----------------|--------------------------|----------------|----------------|
| `kiwi`   | **Kiwi-Edit**      | Wan2.2-5B + Qwen2.5-VL-3B | **MIT**        | #1 open on OpenVE-Bench (3.02); cleanest Diffusers API. **Default pick.** |
| `live`   | **LIVEditor-14B**  | Wan2.2-T2V-A14B          | check upstream | Only 2026 model claiming wins on EditVerseBench + IVEBench + VIE-Bench at once. 96 GB runs it single-GPU. |
| `ditto`  | **Ditto / Editto** | Wan2.1-VACE-14B (LoRA)   | CC BY-NC-SA    | Independent IVEBench leader for instruction-following (CVPR'26 Highlight). Research only. |
| `lucy`   | **Lucy Edit Dev**  | Wan2.2-5B                | Non-commercial | Fast, tiny, clean `LucyEditPipeline`. Good for quick localized edits. |
| `seedvr2`| **SeedVR2 7B**     | DiT upscaler             | —              | Temporally-consistent upscale to 2K/4K (`--upscale`). |

> ⚠️ **License note.** Ditto and Lucy Edit are **non-commercial**. LIVEditor's
> license is unstated — verify before any commercial use. Only **Kiwi-Edit (MIT)**
> is safe for commercial deployment. This bundle assumes the research/personal use
> you selected.

## Hardware target & gotchas (Blackwell / sm_120)

- Confirmed: RTX PRO 6000 Blackwell = **96 GB GDDR7**, hardware FP4/FP8, ~1.8 TB/s.
- **Requires CUDA 12.8+ and a PyTorch build with `sm_120` support** (stable wheels
  fail with "no kernel image"). `install.sh` pins a working nightly.
- **SageAttention 2.2** is the practical attention accelerator (FlashAttention is
  hard to build on Blackwell). Triton backend can produce black frames with Wan —
  the installer selects the CUDA backend.
- 96 GB lets you skip GGUF/fp8 quantization and run **fp16/bf16 full precision**,
  long context windows, and keep multiple models resident.

## Install

```bash
cd video_edit
bash install.sh            # creates ./venv, installs torch nightly + deps, clones model repos
python download_models.py  # downloads weights into ./weights (large: 5B + 14B models)
```

See [`install.sh`](install.sh) for the exact pinned versions and per-repo clone steps.

## Usage

```bash
# Activate the environment created by install.sh
source venv/bin/activate

# Best-quality MIT model (default)
python edit.py --model kiwi --input in.mp4 --prompt "make it a snowy night scene" --output out.mp4

# Flex the 96 GB card with the 14B model
python edit.py --model live --input in.mp4 --prompt "turn the car into a vintage red convertible" --output out.mp4

# Reference-guided edit (garment/object from a reference image)
python edit.py --model kiwi --input in.mp4 --prompt "replace her dress with this" \
    --reference ref.png --output out.mp4

# Edit then upscale to 4K
python edit.py --model live --input in.mp4 --prompt "cyberpunk neon city" --output out.mp4 --upscale

# A/B the same clip across all models into ./compare/
python edit.py --compare-all --input in.mp4 --prompt "make it autumn" --output compare/
```

Run `python edit.py --help` for all flags. Each backend lives in
[`backends/`](backends/) and maps these unified flags onto the upstream model's
own inference entrypoint, so upstream updates are easy to track.

## Pipeline

```
input.mp4 ──► [edit backend: kiwi | live | ditto | lucy] ──► edited.mp4
                                                              │
                                              (--upscale) ────▼
                                                       [SeedVR2 7B] ──► out_4k.mp4
```

## Tips for good prompt edits

- Use action verbs: **Replace / Change / Transform to / Add / Make it**.
- 20–30 word prompts work best; describe the *target*, not the *difference*.
- Keep clips to ~81 frames per chunk for best temporal consistency; longer clips
  are auto-chunked by `edit.py`.
- Prefer localized edits (wardrobe, object swap, scene/style) over global geometry
  changes — that's where current open models are strongest.
