"""Ditto/Editto backend — Wan2.1-VACE-14B + editing LoRA (research only).

Ditto (HKUST + Ant, CVPR'26 Highlight) is the independent IVEBench leader for
instruction-following. It applies an editing LoRA on top of Wan2.1-VACE-14B.

License: CC BY-NC-SA 4.0 — NON-COMMERCIAL, research use only.
"""
from __future__ import annotations

from .base import Backend, EditRequest, python_exe

ENTRYPOINTS = ["infer_ditto.py", "inference.py", "scripts/infer_ditto.py"]


class DittoBackend(Backend):
    def run(self, req: EditRequest):
        self._check_assets()
        script = self._find_entrypoint(ENTRYPOINTS)

        cmd = [
            python_exe(), str(script.name),
            "--lora_path", str(self.spec.weights_path),
            "--input_video", str(req.input),
            "--prompt", req.prompt,
            "--output", str(req.output),
            "--num_frames", str(req.frames),
            "--height", str(req.height),
            "--width", str(req.width),
            "--steps", str(req.steps),
            "--seed", str(req.seed),
        ]

        req.output.parent.mkdir(parents=True, exist_ok=True)
        self._run_subprocess(cmd, cwd=self.spec.vendor_path)
        return req.output
