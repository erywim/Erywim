# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 这是什么 / What this repo is

这是一个 GitHub 个人主页 README 仓库（GitHub profile README repository）：`README.md` 会直接渲染在 GitHub 用户主页上（https://github.com/erywim）。

- 用户：erywim（GitHub 用户名），仓库名 `Erywim` 必须与用户名一致，否则 GitHub 不会把它当作 profile README 渲染。
- 仓库位于 `git@github.com:erywim/Erywim.git`，分支 `master`。

## 现状 / Current state

- 项目文件：`README.md`（已定制为「涂鸦 / 手绘 / 像素风」个人主页 README）+ `assets/*.svg`（本地静态插画）+ `tech-stack.json` + `scripts/generate.py`。
- **没有任何构建、测试、lint 或 CI 工具链** —— 这是一个纯 Markdown + 静态 SVG 项目，无需 `npm install` / `build` / `test`；唯一的工具是标准库 `python3`。
- 也没有 `.gitignore`、配置文件或子目录。

## README.md 结构

README 全部由 GitHub 支持的静态格式构成（Markdown + `<img>` 引用本地 SVG + HTML 注释），无外部依赖、无构建步骤：

- **assets/ 本地 SVG**：所有插画都是独立的 `.svg` 文件，README 里用 `<img src="./assets/xx.svg">` 引用。这是刻意的设计——**内联 SVG 在 GitHub README 渲染时会被 HTML 过滤器剥掉部分标签（`<style>`、`<defs>`/`<use>`），导致显示不全，所以一律走本地文件 + `<img>`**。只有「需要动态变化」的内容（如 github-readme-stats、shields 徽章）才用外链 URL。
- **hero.svg**：手绘波浪边框 + 像素画（机器人/火箭/爱心/雏菊/闪星）+ 手写标题。**文字由脚本从数据生成**（`tech-stack.json` 的 `hero` 段，见下节）；装饰层是固定模板。
- **关于我**：Markdown 段落（用户可直接改文字）。
- **card-fullstack.svg**：技术栈卡片（单张「全栈 · Fullstack」，按分类分组：AI 应用 / 后端 / 前端 / 中间件 / 并发与网络），结构 = 手绘波浪边框 + 左侧导轨（"FS" 大字 + 像素图标 + 波浪线）+ 轻微旋转的贴纸式标签 chips。**这张卡片不是手写的，由脚本从数据生成**（见下节）。
- **divider.svg**（8-bit 日式 RPG 像素场景分隔条：深蓝夜空 + 月亮/云/星星 + 中央像素城堡 + 两侧雪山 + 草地；纯 `<rect>` 像素绘制，出现 2 次）、**heading-about.svg**、**heading-stack.svg**、**heading-stats.svg**、**signoff.svg**（这些是手工绘制的静态 SVG，不参与数据生成）。

## SVG 生成器（hero + 卡片）

`tech-stack.json`（数据源）→ `scripts/generate.py`（排版引擎）→ `assets/hero.svg` + `assets/card-fullstack.svg`（产物）。

- **改内容的流程**：编辑 `tech-stack.json`（`hero` 段改顶部文字，`fullstack` 段改技术栈标签/分类）→ 运行 `python3 scripts/generate.py` → 重新生成 hero.svg + 卡片 SVG → 提交。**不要手改 `hero.svg` / `card-fullstack.svg`**，下次跑脚本会被覆盖。
- **hero 段**：字段 `greeting / name / tagline / sub1 / sub2`，支持空字符串隐藏对应行；名字/标语会自动按宽度缩字号防溢出（名字避让右上火箭）。装饰层（深色像素面板 + 内联像素精灵：机器人/火箭/爱心/雏菊/闪星）是固定模板，不随数据变。
- 排版引擎自动做：按等宽字体宽度估算标签尺寸（CJK≈1em、emoji≈1.2em、其余≈0.62em）、自动换行、自动算卡片高度。**标签是像素风格**：无圆角、无旋转、深底 `#26345A` + 黑边框 + 米白等宽大写文字。
- JSON 结构：每张卡片一个 key（key 决定输出文件名 `card-<key>.svg`）→ `{rail, title, en, accent, icon, blocks[]}`；`rail` 是左侧导轨大字（本仓库用 `"FS"`）；`en` 为空字符串则不显示右上角小字；`icon` 可选 `chip|star|db|heart`；block 用 `label/color/tags`，或 `note`（渲染成整条横幅）。
- 数据校验：生成后跑 `xmllint --noout assets/card-fullstack.svg`。
- 已知边界：估算宽度偏保守，超长的标签会自动缩小字号（13→12→11.5）并可能独占一行；不要放比 "Prompt / Context / Harness Engineering" 更长的标签。
- **数据区（底部，外链动态）**：唯一的动态例外——两张 `github-readme-stats.vercel.app` 实时卡片，配色已调成与深色主题一致（`bg_color=1F2A44`、`title_color=FF8A7A`、`text_color=F5EFE0`、`icon_color=4FA39A`、`border_radius=0`、`hide_border=true`）。用户改用户名时同步更新两处 URL 的 `username=erywim`。

## 修改时的注意事项

- 改动 `README.md` 后，推送回 `master`（GitHub 只渲染默认分支上的 `README.md`）；新增/修改 `assets/` 下的 SVG 也要一并提交。
- **hero.svg / card-fullstack.svg 由脚本生成，别手改**；标题/分隔条/签名 SVG 是手工静态的，改文案需同步调坐标（文字用 `text-anchor="middle"` 居中于 rect）。字体大小用 `font-size`，CJK 按 ~1em/字估算宽度。
- **SVG 必须是良构 XML**：标签要闭合、`&` 要写成 `&amp;`。修改后可用 `xmllint --noout assets/*.svg` 校验。
- **像素字体用系统等宽字体，不能依赖外部字体**：SVG 经 `<img>` 加载时被 GitHub CSP 禁止拉外部资源，所以字体栈用 `'Monaco','Menlo','Consolas','Courier New',monospace`。不要加 `<style>@import(url)` 这类外链字体。
- **设计系统（深色日式 RPG UI）**：面板黑边框 `#0A0E18`、深蓝面板 `#1F2A44`、面板高光/导轨 `#2A3A5E`、标签底 `#26345A`、主文字米白 `#F5EFE0`、次要文字 `#A8B4D0`。这些常量定义在 `scripts/generate.py` 顶部，全局替换即可换色。
- **精灵必须内联，不要用 `<use>`**：`<use href>` 在某些渲染器（如 QuickLook）下不渲染；hero 精灵是直接从 `<defs>` 抽取内联的（`SPRITES_INLINE`），新加像素画时也要直接写 `<rect>`。
- `<!-- -->` 注释块不会显示在主页上，可用于保留说明文字。
- 若未来加入动态生成（如 GitHub Actions 定时更新、readme-stats 等），需同时更新本文件以记录构建/部署方式。
