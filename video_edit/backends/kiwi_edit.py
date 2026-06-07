"""Kiwi-Edit backend (default, MIT) — drives the upstream diffusers demo.

Kiwi-Edit (showlab) ships ``diffusers_demo.py`` plus native diffusers-format
weights (``linyq/kiwi-edit-5b-*``). We invoke the upstream script so we always
match its exact pipeline, including the Qwen2.5-VL instruction planner.

If you supply ``--reference``, the reference-conditioned weights variant is used.

Best evidence-backed open editor as of June 2026 (OpenVE-Bench #1) and the only
commercial-safe pick (MIT).
"""
from __future__ import annotations

from .base import Backend, EditRequest, python_exe

# Candidate upstream entrypoints, most-specific first. Update if the repo moves.
ENTRYPOINTS = ["diffusers_demo.py", "inference.py", "scripts/diffusers_demo.py"]


class KiwiEditBackend(Backend):
    def run(self, req: EditRequest):
        self._check_assets()
        script = self._find_entrypoint(ENTRYPOINTS)

        # Use the reference-guided weights when a reference image is given.
        weights = self.spec.weights_path
        if req.reference is not None:
            ref_weights = weights / "reference"
            if ref_weights.exists():
                weights = ref_weights

        cmd = [
            python_exe(), str(script.name),
            "--model_path", str(weights),
            "--input_video", str(req.input),
            "--prompt", req.prompt,
            "--output_path", str(req.output),
            "--num_frames", str(req.frames),
            "--height", str(req.height),
            "--width", str(req.width),
            "--num_inference_steps", str(req.steps),
            "--seed", str(req.seed),
            "--dtype", req.dtype,
        ]
        if req.reference is not None:
            cmd += ["--reference_image", str(req.reference)]

        req.output.parent.mkdir(parents=True, exist_ok=True)
        self._run_subprocess(cmd, cwd=self.spec.vendor_path)
        return req.output
