"""LIVEditor-14B backend — drives the upstream single-script inference.

LIVEditor (xie-lab, ICML 2026) is a Wan2.2-T2V-A14B editor with in-context
sparse attention; it claims simultaneous wins on EditVerseBench, IVEBench and
VIE-Bench. The 14B weights run on ONE RTX PRO 6000 (96 GB) — no multi-GPU split
needed — which is exactly what this hardware is for.

License unstated upstream — verify before any commercial use.
"""
from __future__ import annotations

from .base import Backend, EditRequest, python_exe

ENTRYPOINTS = ["inference.py", "infer.py", "scripts/inference.py"]


class LIVEditorBackend(Backend):
    def run(self, req: EditRequest):
        self._check_assets()
        script = self._find_entrypoint(ENTRYPOINTS)

        cmd = [
            python_exe(), str(script.name),
            "--ckpt", str(self.spec.weights_path),
            "--input", str(req.input),
            "--prompt", req.prompt,
            "--output", str(req.output),
            "--num_frames", str(req.frames),
            "--height", str(req.height),
            "--width", str(req.width),
            "--steps", str(req.steps),
            "--seed", str(req.seed),
        ]
        if req.reference is not None:
            cmd += ["--reference", str(req.reference)]
        if req.enhance_prompt:
            cmd += ["--use_pe"]  # upstream prompt-enhancer flag, if present

        req.output.parent.mkdir(parents=True, exist_ok=True)
        self._run_subprocess(cmd, cwd=self.spec.vendor_path)
        return req.output
