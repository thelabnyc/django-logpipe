#!/usr/bin/env python3
"""
Copy third-party files the docs site serves itself into the docs folder.

The package versions and their sha512 integrity hashes come from
docs-vendor/package-lock.json, which Renovate keeps up to date, so this needs
no Node. Each package's files are listed under "docsAssets" in
docs-vendor/package.json, as shell-style patterns for paths inside the
package, where "*" also matches "/".
"""

from argparse import ArgumentParser
from fnmatch import fnmatch
from pathlib import Path, PurePosixPath
from urllib.request import urlopen
import base64
import hashlib
import io
import json
import shutil
import sys
import tarfile

REGISTRY = "https://registry.npmjs.org/"
STAMP = ".integrity"


def read_json_object(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: expected a JSON object")
    return data


def read_assets(manifest: Path) -> dict[str, list[str]]:
    assets = read_json_object(manifest / "package.json").get("docsAssets")
    if not isinstance(assets, dict) or not all(isinstance(paths, list) and all(isinstance(p, str) for p in paths) for paths in assets.values()):
        raise SystemExit(f"{manifest}/package.json: docsAssets must map names to lists of paths")
    return {str(name): [str(p) for p in paths] for name, paths in assets.items()}


def locked_package(lock: dict[str, object], name: str) -> tuple[str, str]:
    packages = lock.get("packages")
    entry = packages.get(f"node_modules/{name}") if isinstance(packages, dict) else None
    if not isinstance(entry, dict):
        raise SystemExit(f"{name} isn't in package-lock.json")
    resolved, integrity = entry.get("resolved"), entry.get("integrity")
    if not isinstance(resolved, str) or not resolved.startswith(REGISTRY):
        raise SystemExit(f"{name}: lockfile must resolve to {REGISTRY}")
    if not isinstance(integrity, str) or not integrity.startswith("sha512-"):
        raise SystemExit(f"{name}: lockfile has no sha512 integrity")
    return resolved, integrity


def download(url: str, integrity: str) -> bytes:
    with urlopen(url, timeout=120) as response:
        body: bytes = response.read()
    digest = base64.b64encode(hashlib.sha512(body).digest()).decode()
    if f"sha512-{digest}" != integrity:
        raise SystemExit(f"{url} doesn't match the lockfile's integrity hash")
    return body


def extract(tarball: bytes, patterns: list[str], dest: Path) -> set[str]:
    copied: set[str] = set()
    with tarfile.open(fileobj=io.BytesIO(tarball), mode="r:gz") as archive:
        for member in archive.getmembers():
            parts = PurePosixPath(member.name).parts
            if not member.isfile() or len(parts) < 2 or ".." in parts:
                continue
            path = "/".join(parts[1:])
            source = archive.extractfile(member)
            if source is None or not any(fnmatch(path, p) for p in patterns):
                continue
            target = dest.joinpath(*parts[1:])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read())
            copied.add(path)
    return copied


def vendor(manifest: Path, dest: Path) -> None:
    lock = read_json_object(manifest / "package-lock.json")
    for name, patterns in read_assets(manifest).items():
        resolved, integrity = locked_package(lock, name)
        package_dest = dest / name
        stamp = package_dest / STAMP
        stamp_text = json.dumps([integrity, patterns])
        if stamp.is_file() and stamp.read_text() == stamp_text:
            continue
        print(f"Vendoring {resolved}")
        if package_dest.exists():
            shutil.rmtree(package_dest)
        copied = extract(download(resolved, integrity), patterns, package_dest)
        for pattern in patterns:
            if not any(fnmatch(path, pattern) for path in copied):
                raise SystemExit(f"{name}: nothing matches {pattern}")
        stamp.write_text(stamp_text)


def main() -> int:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("docs-vendor"))
    parser.add_argument("--dest", type=Path, default=Path("docs/vendor"))
    args = parser.parse_args()
    manifest: Path = args.manifest
    dest: Path = args.dest
    vendor(manifest, dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
