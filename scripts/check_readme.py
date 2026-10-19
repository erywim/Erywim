#!/usr/bin/env python3
"""检查 README 引用的本地图片，并确认 HTML 图片都有 alt。"""

import os
import re
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")


def main():
    with open(README, encoding="utf-8") as source:
        readme = source.read()

    errors = []

    for relative_path in sorted(set(re.findall(r"assets/[A-Za-z0-9._/-]+", readme))):
        if not os.path.isfile(os.path.join(ROOT, relative_path)):
            errors.append(f"README 引用了不存在的图片：{relative_path}")

    for alt in re.findall(r"<img\b[^>]*\balt=\"([^\"]*)\"", readme):
        if not alt.strip():
            errors.append("README 中存在 alt 为空的图片")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1

    print("README check passed: local images and alt text are valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
