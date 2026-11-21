#!/usr/bin/env python3
"""Entry point for the make.fun competition
"the-passport-page-of-a-countr-2-20261121-0318".

Writes the passport spread to /output/entry.png. The image is rendered
by build_passport.py (PIL, run at build time) and shipped as entry.png;
this entrypoint is stdlib-only and works offline in the grader sandbox.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dest)
    size = os.path.getsize(dest)
    assert size <= 1048576, f"entry.png over 1 MiB: {size} bytes"
    print(f"wrote {dest} ({size} bytes)")


if __name__ == "__main__":
    main()
