"""Lucy-Edit-Dev backend — native Diffusers pipeline (no GUI, no nodes).

Lucy ships a first-class ``LucyEditPipeline`` in diffusers, so this is the
cleanest fully-scripted path. 5B model — trivially fits 96 GB in fp32.

License: NON-COMMERCIAL (Decart). Research/personal use only.
"""
from __future__ import annotations

import torch

from .base import Backend, EditRequest
from . import videoio


_DTYPES = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}


class LucyEditBackend(Backend):
    _pipe = None

    def _load(self, dtype: str):
        if self._pipe is not None:
            return self._pipe
        from diffusers import LucyEditPipeline
        from diffusers import AutoencoderKLWan

        torch_dtype = _DTYPES[dtype]
        path = str(self.spec.weights_path)
        # Wan VAE is kept in fp32 for stability even when the DiT runs lower.
        vae = AutoencoderKLWan.from_pretrained(path, subfolder="vae", torch_dtype=torch.float32)
        pipe = LucyEditPipeline.from_pretrained(path, vae=vae, torch_dtype=torch_dtype)
        pipe.to("cuda")
        self._pipe = pipe
        return pipe

    def run(self, req: EditRequest):
        if not self.spec.weights_path.exists():
            raise FileNotFoundError(
                f"Lucy weights missing at {self.spec.weights_path}. "
                f"Run: python download_models.py lucy"
            )
        pipe = self._load(req.dtype)

        fps = req.fps or int(round(videoio.probe_fps(req.input)))
        frames = videoio.read_frames(req.input)
        out_frames: list = []

        # Lucy is tuned for ~81-frame windows; auto-chunk longer clips.
        for start, end in videoio.chunk_indices(len(frames), req.frames):
            window = frames[start:end]
            result = pipe(
                prompt=req.prompt,
                video=window,
                height=req.height,
                width=req.width,
                num_inference_steps=req.steps,
                generator=torch.Generator(device="cuda").manual_seed(req.seed),
            )
            out_frames.extend(result.frames[0])

        return videoio.write_frames(out_frames, req.output, fps=fps)
