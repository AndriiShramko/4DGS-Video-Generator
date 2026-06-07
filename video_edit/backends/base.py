"""Shared backend interface and helpers.

Each model backend subclasses :class:`Backend` and implements :meth:`run`.
Two integration styles are supported:

* **Native** (Lucy Edit) — imports a Diffusers pipeline directly.
* **Vendored CLI** (Kiwi-Edit, LIVEditor, Ditto, SeedVR2) — shells out to the
  upstream repo's own inference entrypoint cloned in ``vendor/``. This keeps us
  robust to each repo's internal API and easy to track against upstream.

The flag maps in the vendored backends are written from each repo's documented
interface (June 2026). If an upstream repo renames a flag, adjust the
``cmd``/``ENTRYPOINTS`` list in that one backend file — nothing else changes.
"""
from __future__ import annotations

import dataclasses
import subprocess
import sys
from pathlib import Path

import config


@dataclasses.dataclass
class EditRequest:
    """A single edit job, populated from the CLI in edit.py."""
    input: Path
    prompt: str
    output: Path
    reference: Path | None = None   # optional reference image for r-v2v edits
    frames: int = 81
    height: int = 480
    width: int = 832
    steps: int = 30
    seed: int = 42
    fps: int | None = None          # output fps; None = keep source fps
    dtype: str = "bf16"             # bf16/fp16/fp32 — 96 GB can afford fp32
    enhance_prompt: bool = False    # use an upstream LLM prompt-enhancer if available
    extra: dict = dataclasses.field(default_factory=dict)


class Backend:
    """Base class for all editing/upscaling backends."""

    spec: config.ModelSpec

    def __init__(self, spec: config.ModelSpec):
        self.spec = spec

    # --- to be implemented by subclasses ---------------------------------
    def run(self, req: EditRequest) -> Path:
        raise NotImplementedError

    # --- shared helpers ---------------------------------------------------
    def _check_assets(self) -> None:
        """Verify the upstream repo and weights exist before running."""
        if not self.spec.vendor_path.exists():
            raise FileNotFoundError(
                f"{self.spec.name}: upstream repo missing at {self.spec.vendor_path}.\n"
                f"Run install.sh (it clones {self.spec.git_repo})."
            )
        if not self.spec.weights_path.exists():
            raise FileNotFoundError(
                f"{self.spec.name}: weights missing at {self.spec.weights_path}.\n"
                f"Run: python download_models.py {self.spec.key}"
            )

    def _find_entrypoint(self, candidates: list[str]) -> Path:
        """Return the first existing upstream script from a candidate list."""
        for rel in candidates:
            p = self.spec.vendor_path / rel
            if p.exists():
                return p
        raise FileNotFoundError(
            f"{self.spec.name}: none of the expected entrypoints exist under "
            f"{self.spec.vendor_path}: {candidates}. The upstream repo layout may "
            f"have changed — update ENTRYPOINTS in backends/{self.spec.backend}.py."
        )

    def _run_subprocess(self, cmd: list[str], cwd: Path) -> None:
        """Run an upstream inference command with the vendor repo on PYTHONPATH."""
        printable = " ".join(str(c) for c in cmd)
        print(f"  [{self.spec.key}] $ {printable}")
        env = _vendor_env(cwd)
        proc = subprocess.run(cmd, cwd=str(cwd), env=env)
        if proc.returncode != 0:
            raise RuntimeError(
                f"{self.spec.name} inference failed (exit {proc.returncode}). "
                f"Command: {printable}"
            )


def _vendor_env(cwd: Path) -> dict:
    import os

    env = dict(os.environ)
    # Make the vendor repo importable and force the same Python interpreter.
    env["PYTHONPATH"] = os.pathsep.join(
        [str(cwd), env.get("PYTHONPATH", "")]
    ).strip(os.pathsep)
    return env


def python_exe() -> str:
    """Path to the current interpreter (the venv python after activation)."""
    return sys.executable
