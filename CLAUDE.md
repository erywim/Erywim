# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 这是什么

这是 GitHub 个人主页仓库，`README.md` 会渲染在 https://github.com/erywim 的个人主页上。仓库名 `Erywim` 必须与 GitHub 用户名一致，默认分支是 `master`。

## 当前结构

- `README.md`：主页内容。除 Hero 外全部使用原生 Markdown，保证可搜索、可复制、可换行，并跟随 GitHub 明暗主题。
- `assets/hero-light.svg`、`assets/hero-dark.svg`：同一套「Famicom 冒险手册」Hero 的浅色和深色版本，由脚本生成。
- `tech-stack.json`：Hero 文案与关于页六类、共 50 项技术栈的校验来源；README 摘要仍按内容需要手动编写。
- `scripts/generate.py`：生成两张 Hero SVG。
- `scripts/check_readme.py`：检查 README 是否覆盖全部技术项，并确认本地图片存在。
- `.gitignore`：忽略 Python 缓存和 macOS 临时文件。

本项目没有 npm、构建流程或测试框架，只依赖 Python 3 标准库。

## 内容结构

`README.md` 的顺序是：

1. Hero：姓名、角色、价值主张和三个主入口。
2. `NOW / 现在`：正在做、正在学、关注方向和可聊话题。
3. `PROJECTS / 项目`：只放可公开验证的项目。
4. `TRACK RECORD / 经历`：三段公开职业与教育经历。
5. `WHAT I DO / 我在做什么`：四项能力支柱。
6. `TOOLBOX / 技术栈`：四到五组摘要，`<details>` 内保留完整六类清单。
7. `OFF-SCREEN / 工作之外`：动漫、摄影、游戏和个人站入口。
8. `CONTACT / 联系`：个人站、GitHub、Email。

不要恢复 badge 墙、GitHub 动态统计卡、RPG 角色游行或整页大图。用户已经明确不想要动态统计；主页的核心信息必须保留为正文文字。

## 修改流程

修改 Hero 文案：

1. 编辑 `tech-stack.json` 的 `profile` 段。
2. 运行 `python3 scripts/generate.py`。
3. 运行 `python3 scripts/check_readme.py`。
4. 运行 `xmllint --noout assets/hero-light.svg assets/hero-dark.svg`。

增删技术栈：

1. 编辑 `tech-stack.json` 的 `techStack` 数组。
2. 同步更新 `README.md` 的摘要和 `<details>` 清单。
3. 运行 `python3 scripts/check_readme.py`，确保 6 类、50 项和全部条目都被覆盖。
4. 如果关于页也变更，以 https://erywim.github.io/about/ 为准同步数据。

## GitHub 渲染约束

- Profile README 的桌面内容宽度约为 846px，375px 手机下实际约 293px。Hero 按 840×220 设计，只承载大字号身份信息；其余内容全部是原生 Markdown。
- GitHub 会过滤内联 `<svg>`、`<script>`、`<style>`、`<iframe>` 和自定义样式。图片必须走仓库内的独立 `.svg` 文件。
- `<picture>` 的 `<source media="(prefers-color-scheme: ...)">` 用于明暗主题切换。fallback `<img>` 只写 `width`，不要写 `height`，否则 GitHub 的 `themed-picture` 包装可能造成窄屏纵向拉伸。
- SVG 通过 `<img>` 加载时是独立图片文档，GitHub CSP 不允许外部字体、外部图片、脚本或 `currentColor` 依赖。所有绘制和字体都要自包含。
- SVG 内的系统字体栈只做视觉兜底，不保证跨平台像素级一致。关键信息不能只放在图片里。
- 装饰图片必须有非空 alt；GitHub 会自动把图片包进链接，空 alt 会形成无名称链接。
- 同仓库图片缓存约 5 分钟。推送后如果线上仍是旧图，先等待缓存刷新再判断是否失败。

## 设计系统

视觉方向是「RPG Editorial」：个人站负责沉浸式 RPG 体验，GitHub 主页只保留一枚克制、可识别的冒险手册 Hero。

- 浅色：纸面 `#F3E9CE`、墨蓝 `#1C2340`、朱红 `#B64235`、青绿 `#2F7F78`、金色 `#A77A2A`。
- 深色：深蓝 `#12172A`、暖米白 `#F4EAD2`、珊瑚红 `#FF7A5C`、亮青绿 `#7AD9D0`、金色 `#E9B45E`。
- Hero 右侧是一条从像素史莱姆出发、经过四个节点抵达旗帜的路线；路线只表达「从想法到完成」，不承载需要阅读的微文案。
- 不要使用大面积纯白面板；不要再增加第二套视觉系统。正文的视觉节奏来自章节编号、短段落、inline code 和留白。

## 上线

修改后提交到 `master` 并推送。GitHub 只会渲染默认分支上的 `README.md`，新增的 Hero 资源也必须一起提交。推送后在真实页面检查：

- 桌面与 390px 手机宽度；
- GitHub 浅色和深色主题；
- Hero 是否切换正确、无裁切；
- 所有链接可点击，图片无 404；
- `details` 展开后完整技术栈可读。
