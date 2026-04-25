from __future__ import annotations

import importlib.abc
import importlib.machinery
import importlib.util
import sys
from pathlib import Path


class _StagedSrcFinder(importlib.abc.MetaPathFinder):
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.src_root = (self.root / "src").resolve()

    def find_spec(self, fullname: str, path: object = None, target: object = None):  # type: ignore[override]
        if fullname == "src":
            return importlib.machinery.PathFinder.find_spec(fullname, [str(self.root)])
        if fullname.startswith("src."):
            return importlib.machinery.PathFinder.find_spec(fullname, [str(self.src_root)])
        return None


def _install_staged_src_finder() -> Path | None:
    root = Path(__file__).resolve().parent
    init_path = root / "src" / "__init__.py"
    if not init_path.is_file():
        return None

    finder = _StagedSrcFinder(root)
    if not any(type(existing).__name__ == "_StagedSrcFinder" for existing in sys.meta_path):
        sys.meta_path.insert(0, finder)
    return init_path


def _force_staged_src(init_path: Path | None) -> None:
    if init_path is None:
        return

    current = sys.modules.get("src")
    current_file = Path(getattr(current, "__file__", "")) if current is not None else None
    if current_file is not None:
        try:
            if current_file.resolve() == init_path.resolve():
                return
        except OSError:
            pass

    spec = importlib.machinery.PathFinder.find_spec("src", [str(init_path.parent.parent)])
    if spec is None or spec.loader is None:
        return

    module = importlib.util.module_from_spec(spec)
    sys.modules["src"] = module
    spec.loader.exec_module(module)


_force_staged_src(_install_staged_src_finder())
