#!/usr/bin/env python3
import os
import sys
import argparse
import zipfile
import urllib.request
from pathlib import Path


def download(url: str, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as r, open(dest, "wb") as f:
        f.write(r.read())


def extract(zip_path: Path, dest_dir: Path):
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)


def main():
    parser = argparse.ArgumentParser(description="Consume full_deploy bundle without Conan")
    parser.add_argument("--url", required=True, help="URL to full_deploy.zip (GitHub Releases/Cloudsmith)")
    parser.add_argument("--dest", default=".deps", help="Destination directory for dependencies")
    args = parser.parse_args()

    dest = Path(args.dest)
    zip_path = dest.with_suffix(".zip")

    print(f"Downloading: {args.url}")
    download(args.url, zip_path)

    print(f"Extracting to: {dest}")
    extract(zip_path, dest)

    print("Environment activation (example):")
    bin_dir = dest / "full_deploy" / "bin"
    lib_dir = dest / "full_deploy" / "lib"
    print(f"  - Add to PATH: {bin_dir}")
    print(f"  - Add to LD_LIBRARY_PATH/DYLD_LIBRARY_PATH: {lib_dir}")

    print("Done.")


if __name__ == "__main__":
    main()
