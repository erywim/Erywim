# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 这是什么

这是 GitHub 个人主页仓库，`README.md` 会渲染在 https://github.com/erywim 的个人主页上。仓库名 `Erywim` 必须与 GitHub 用户名一致，默认分支是 `master`。

## 当前结构

- `README.md`：常规 GitHub Profile 布局，包含欢迎横幅、简介、技术徽章、项目、GitHub 数据、贡献蛇和联系方式。
- `assets/hero.svg`：自包含的深色动态横幅，带打字、扫描线、浮动粒子和终端卡片动效。
- `tech-stack.json`：Hero 文案与关于页六类、共 50 项技术栈的校验来源。
- `scripts/generate.py`：生成 `assets/hero.svg`。
- `scripts/check_readme.py`：检查 README 的完整技术栈、本地图片和图片 alt。
- `.github/workflows/snake.yml`：每天生成贡献蛇并发布到 `output` 分支。
- `.gitignore`：忽略 Python 缓存和 macOS 临时文件。

本项目没有 npm、构建流程或测试框架，只依赖 Python 3 标准库和 GitHub Actions。

## 内容结构

`README.md` 的顺序是：

1. 动态 Hero。
2. 网站、Email、GitHub 徽章。
3. `About Me`：当前在做什么、背景、学习方向、兴趣。
4. `Tech Stack`：AI、后端、前端的代表性徽章，`<details>` 内保留完整 50 项。
5. `Featured Projects`：只放可公开验证的项目。
6. `GitHub Stats`：GitHub Readme Stats 与 streak-stats。
7. `Contribution Snake`：读取 `output` 分支的明暗两套贡献蛇 SVG。
8. `Let's Connect`：网站、Email、GitHub。

不要恢复博客式的 RPG 角色卡、冒险路线或长段职业叙事。GitHub 主页应保持常规 Profile 结构，视觉重点集中在一个动态 Hero。

## 修改流程

修改 Hero 文案：

1. 编辑 `tech-stack.json` 的 `profile` 段。
2. 运行 `python3 scripts/generate.py`。
3. 运行 `python3 scripts/check_readme.py`。
4. 运行 `xmllint --noout assets/hero.svg`。

增删技术栈：

1. 编辑 `tech-stack.json` 的 `techStack` 数组。
2. 同步更新 `README.md` 的徽章和 `<details>` 清单。
3. 运行 `python3 scripts/check_readme.py`，确保 6 类、50 项和全部条目都被覆盖。
4. 如果关于页也变更，以 https://erywim.github.io/about/ 为准同步数据。

## GitHub 渲染约束

- Profile README 的桌面内容宽度约为 846px，375px 手机下实际约 293px。Hero 按 880×240 设计，只承载大字号身份信息；其他内容使用原生 Markdown。
- GitHub 会过滤内联 `<svg>`、`<script>`、`<style>`、`<iframe>` 和自定义样式。图片必须走仓库内的独立 `.svg` 文件。
- `<img>` 加载的 SVG 是独立图片文档。GitHub raw 的 CSP 允许 SVG 内联样式与动画，但禁止外部字体、外部图片、脚本或 `currentColor` 依赖。
- Hero 使用 SMIL 动画，目前在 Chrome 中通过真实 GitHub 页面验证过打字和扫描线动效。
- 外部统计卡依赖第三方服务，可能被 Camo 缓存或短时不可用；不要让它们成为核心信息的唯一来源。
- 贡献蛇由 `.github/workflows/snake.yml` 生成到 `output` 分支，README 通过 raw URL 读取，不要手写或提交生成结果。
- 装饰图片必须有非空 alt；GitHub 会自动把图片包进链接，空 alt 会形成无名称链接。
- 同仓库图片缓存约 5 分钟，外部图片缓存可能更久。推送后如果线上仍是旧图，先等待缓存刷新。

## 设计系统

- Hero 背景：深海军蓝 `#07111F` 到 `#0B1B31`，网格和青色辉光营造终端感。
- 主文字：近白 `#F8FAFC`；打字文本与高亮：青色 `#67E8F9`；提示色：绿色 `#34D399`；状态色：琥珀 `#FBBF24`。
- 动效克制：打字、扫描线、光扫、少量粒子；不要继续增加旋转、闪烁或大面积渐变动画。
- 正文使用 GitHub 原生排版，技术栈用 shields.io 徽章分组，避免再做大面积自绘技能卡。

## 上线

修改后提交到 `master` 并推送。GitHub 只会渲染默认分支上的 `README.md`，Hero 和 workflow 也必须一起提交。推送后检查：

- 1440px 桌面与 390px、320px 手机；
- GitHub 浅色和深色主题；
- Hero 动画是否在 `<img>` 中运行；
- 技术徽章、统计卡和贡献蛇是否加载；
- `<details>` 展开后 50 项技术栈是否可读；
- 所有链接可点击，图片无 404。
