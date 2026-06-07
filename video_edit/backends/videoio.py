"""Tiny video I/O helpers shared across backends (read/write/chunk/probe)."""
from __future__ import annotations

from pathlib import Path


def probe_fps(path: Path) -> float:
    """Return the source video fps (falls back to 24.0)."""
    import imageio.v3 as iio

    try:
        meta = iio.immeta(str(path), plugin="pyav")
        fps = float(meta.get("fps", 0) or 0)
        return fps if fps > 0 else 24.0
    except Exception:
        return 24.0


def read_frames(path: Path):
    """Read a video into a list of HxWx3 uint8 numpy frames."""
    import imageio.v3 as iio

    return list(iio.imiter(str(path), plugin="pyav"))


def write_frames(frames, path: Path, fps: float) -> Path:
    """Write frames to an mp4 (yuv420p, H.264) at the given fps."""
    import imageio.v3 as iio

    path.parent.mkdir(parents=True, exist_ok=True)
    iio.imwrite(
        str(path),
        frames,
        plugin="pyav",
        codec="libx264",
        fps=fps,
        out_pixel_format="yuv420p",
    )
    return path


def chunk_indices(n_frames: int, chunk: int):
    """Yield (start, end) windows of ``chunk`` frames covering ``n_frames``."""
    start = 0
    while start < n_frames:
        yield start, min(start + chunk, n_frames)
        start += chunk
