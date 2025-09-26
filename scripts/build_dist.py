#!/usr/bin/env python3
import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Tuple

API_VERSION_SUBDIR = "v1"

def write_json(path: Path, data: Any, pretty: bool = True) -> None:
    if pretty:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        path.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")

def copy_data_to_dir(src_dir: Path, dst_dir: Path) -> List[Path]:
    copied: List[Path] = []
    for src in src_dir.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(src_dir)
        dst = dst_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(dst)
    return copied

def minify_each_json_in_dir(root_dir: Path) -> List[Path]:
    created: List[Path] = []
    for p in root_dir.rglob("*.json"):
        if p.name.endswith(".min.json"):
            continue
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Skip minifying {p}: {e}")
            continue
        min_path = p.with_name(p.stem + ".min.json")
        write_json(min_path, obj, pretty=False)
        created.append(min_path)
    return created

def build_bundle_flat(root_dir: Path, bundle_name: str = "bundle.json") -> Tuple[Path, Path]:
    merged: Dict[str, Any] = {}
    for p in sorted(root_dir.rglob("*.json")):
        if p.name.endswith(".min.json"):
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                merged.update(data)
            else:
                merged[p.stem] = data
        except Exception as e:
            print(f"Skip bundling {p}: {e}")

    out_pretty = root_dir / bundle_name
    out_min = root_dir / (Path(bundle_name).stem + ".min.json")
    write_json(out_pretty, merged, pretty=True)
    write_json(out_min, merged, pretty=False)
    return out_pretty, out_min

def main():
    ap = argparse.ArgumentParser(description="Copy data/ to dist/v1, create .min.json, bundle.json & bundle.min.json.")
    ap.add_argument("--data-dir", default="data", help="Path to data directory")
    ap.add_argument("--dist-dir", default="dist", help="Path to dist directory")
    args = ap.parse_args()

    data_dir = Path(args.data_dir).resolve()
    dist_root = Path(args.dist_dir).resolve()
    dist_dir = dist_root / API_VERSION_SUBDIR
    dist_dir.mkdir(parents=True, exist_ok=True)

    copied = copy_data_to_dir(data_dir, dist_dir)
    print(f"Copied {len(copied)} files to {dist_dir}")

    mins = minify_each_json_in_dir(dist_dir)
    print(f"Created {len(mins)} minified JSONs")

    bundle_path, bundle_min_path = build_bundle_flat(dist_dir, "bundle.json")
    print(f"Bundle: {bundle_path}")
    print(f"Bundle (min): {bundle_min_path}")

if __name__ == "__main__":
    main()
