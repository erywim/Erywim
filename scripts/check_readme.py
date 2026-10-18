#!/usr/bin/env python3
"""检查 README 是否覆盖完整技术栈，并确认本地图片全部存在。"""

import json
import os
import re
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")
DATA = os.path.join(ROOT, "tech-stack.json")


def main():
    with open(README, encoding="utf-8") as source:
        readme = source.read()
    with open(DATA, encoding="utf-8") as source:
        data = json.load(source)

    errors = []
    categories = data["techStack"]
    items = [item for category in categories for item in category["items"]]
    details_match = re.search(r"<details>.*?</details>", readme, re.DOTALL)

    if len(categories) != 6:
        errors.append(f"技术栈分类应为 6 类，实际为 {len(categories)} 类")
    if len(items) != 50:
        errors.append(f"技术栈应为 50 项，实际为 {len(items)} 项")
    if len(set(items)) != len(items):
        errors.append("技术栈存在重复项")
    if not details_match:
        errors.append("README 缺少完整技术栈的 <details> 区域")
        details = ""
    else:
        details = details_match.group(0)

    for category in categories:
        if f"**{category['name']}** —" not in details:
            errors.append(f"完整技术栈缺少分类：{category['name']}")
        for item in category["items"]:
            if f"`{item}`" not in details:
                errors.append(f"完整技术栈缺少技术项：{item}")

    for relative_path in sorted(set(re.findall(r"assets/[A-Za-z0-9._/-]+", readme))):
        if not os.path.isfile(os.path.join(ROOT, relative_path)):
            errors.append(f"README 引用了不存在的图片：{relative_path}")

    for alt in re.findall(r"<img\b[^>]*\balt=\"([^\"]*)\"", readme):
        if not alt.strip():
            errors.append("README 中存在 alt 为空的图片")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1

    print(f"README check passed: {len(categories)} categories, {len(items)} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
