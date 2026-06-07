"""Backend registry: maps a ModelSpec to its concrete Backend implementation."""
from __future__ import annotations

import config

from .base import Backend, EditRequest
from .kiwi_edit import KiwiEditBackend
from .liveditor import LIVEditorBackend
from .ditto import DittoBackend
from .lucy_edit import LucyEditBackend
from .seedvr2 import SeedVR2Backend

# Keyed by ModelSpec.backend (the module name declared in config.py).
_REGISTRY = {
    "kiwi_edit": KiwiEditBackend,
    "liveditor": LIVEditorBackend,
    "ditto": DittoBackend,
    "lucy_edit": LucyEditBackend,
    "seedvr2": SeedVR2Backend,
}


def load(key: str) -> Backend:
    """Instantiate the backend for a model key (e.g. 'kiwi')."""
    spec = config.get(key)
    try:
        cls = _REGISTRY[spec.backend]
    except KeyError as exc:  # pragma: no cover - guards a config typo
        raise KeyError(
            f"No backend registered for '{spec.backend}' (model {key})."
        ) from exc
    return cls(spec)


__all__ = ["Backend", "EditRequest", "load"]
