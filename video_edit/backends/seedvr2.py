"""SeedVR2-7B backend — temporally-consistent video upscaler (--upscale).

Not an editor: takes an already-edited clip and upscales it to 2K/4K while
preserving temporal consistency. On 96 GB the 7B model runs with large frame
batches (>=5 frames activates SeedVR2's temporal path).
"""
from __future__ import annotations

from pathlib import Path

from .base import Backend, EditRequest, python_exe

ENTRYPOINTS = ["inference.py", "projects/inference_seedvr2.py", "infer.py"]


class SeedVR2Backend(Backend):
    def upscale(self, input_path: Path, output_path: Path, scale: int = 2,
                seed: int = 42) -> Path:
        self._check_assets()
        script = self._find_entrypoint(ENTRYPOINTS)

        cmd = [
            python_exe(), str(script.name),
            "--ckpt", str(self.spec.weights_path),
            "--input", str(input_path),
            "--output", str(output_path),
            "--upscale", str(scale),
            "--seed", str(seed),
        ]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._run_subprocess(cmd, cwd=self.spec.vendor_path)
        return output_path

    def run(self, req: EditRequest):
        # Allow calling SeedVR2 as a standalone "model" too (input -> upscaled).
        return self.upscale(req.input, req.output, seed=req.seed)
