# 滚动地图旅行电子手账 · scroll-map-travel-journal

**制作：阿蓝蓝**

把自己的行程做成一份在电脑浏览器打开的旅行电子手账：左侧地图随滚动展示路线与地点插画，右侧记录照片、文字和便签。

这是供 AI 使用的 Skill，内置网页模板、字体、动画库和制作流程。你不需要另找模板或原项目代码；提供行程即可，照片和笔记可以之后慢慢补。

## 安装

下载 [scroll-map-travel-journal.zip](https://github.com/rayyylam/scroll-map-travel-journal/releases/latest/download/scroll-map-travel-journal.zip)，交给支持 Skill 与文件读写的 AI 工具安装。不同工具的导入方式以各自支持情况为准。

手动安装到 Codex：解压后把 `scroll-map-travel-journal` 文件夹放到 `~/.codex/skills/`，确认其中直接包含 `SKILL.md`，再重新打开会话。自定义 CODEX_HOME 时使用该目录下的 skills 文件夹。

也可以下载或克隆本仓库，把仓库目录作为 Skill 文件夹使用。

## 开始制作

把下面这句话和行程发给 AI：

> 请使用 $scroll-map-travel-journal，按我的行程制作滚动地图旅行手账。请先推荐主要地图点和章节安排，再完成地点插画。照片和笔记我之后自己补。

例如：第一天从 A 城乘火车到 B 城，第二天游览 B 城，第三天乘车到 C 镇，第四天返程。请把地点替换为你的真实目的地，并提供旅行日期。

## 制作流程

1. AI 推荐主要地图点和章节，你一次确认或增删，不必逐个选择所有景点。
2. 选择旅行示意地图（较快）或实际地理比例地图（耗时较长）。
3. 制作可滚动初版，再生成并接入地点插画，检查图标、标签和载具比例。
4. 可选背景美化：保留当前背景，或先看一版质感增强效果。
5. 添加照片、编辑文字和便签，检查保存后的完整作品。

生图需要你当前的 AI 工具具备图片生成能力；本 Skill 不附带模型、账号或 API 额度。无法生图时，AI 会提供完整提示词和参考图，等你交回图片后接入。需要额外安装抠图工具时，会先说明原因和耗时。

## 打开、编辑和分享

- 在电脑上打开完整项目文件夹里的 `index.html`。
- 照片先复制到 `photos/`，再在网页编辑模式选择；封面可以替换。
- “完成”只退出编辑。“保存”会下载新 `index.html`，请备份后放回原项目文件夹替换旧文件。
- 本地制作不默认生成成品 ZIP。需要分享或打包时告诉 AI，它会问是否包含原图。
- 分享 ZIP 包含网页和全部运行素材；朋友在电脑上完整解压后打开 `index.html`。不能只发送 HTML。

地图左下角固定显示整个行程日期。照片选择器只显示旅行照片，不混入地图插画和占位素材。

## 开发与目录

- `SKILL.md`：AI 制作流程入口。
- `references/`：行程组织、地图美术、实现和验收说明。
- `assets/template/`：可离线打开的中性网页模板。
- `assets/style-reference.jpg`：获准随 Skill 提供的复古插画参考。
- `scripts/create_project.py`：使用 Python 标准库创建独立项目，不覆盖已有目录。
- `scripts/check_project.py`：检查本地资源、结构、占位图和地点插画配置。

```bash
python3 scripts/create_project.py --output ./output/my-trip --title "我的旅行" --dates "2030.04.01 – 2030.04.04"
python3 scripts/check_project.py ./output/my-trip --stage draft
# 完成适配和插画后，正式交付前检查：
python3 scripts/check_project.py ./output/my-trip --stage final
```

刚复制的模板尚无行程插画，final 检查会报告未完成。静态检查不能代替地图视觉效果和实际编辑保存测试。不同 AI 模型仍需通过样稿与预览确认效果。

## 署名与许可

原创 Skill 说明、辅助脚本和模板原创贡献采用 [MIT License](LICENSE)，署名 **阿蓝蓝**。随附第三方文件适用各自许可，不因放入本仓库而变更：

- 地图动画参考 [ScrollMap](https://codepen.io/creativeocean/pen/myOVZYO)，作者 **Tom Miller / Creative Ocean**，保留 MIT 许可和原作者署名。
- GSAP / ScrollTrigger：**Webflow / GreenSock**，适用 [GSAP Standard License](https://gsap.com/community/standard-license/)，不属于本项目 MIT 授权范围。
- 宅在家自动笔字体：保留原字体及其名称表授权记录。
- 复古参考海报：获准作为此 Skill 的视觉参考提供，不扩大为其他用途的授权。

完整说明见 [来源与边界](references/sources.md) 和 [第三方许可](assets/template/licenses/第三方说明.md)。用户自己的旅行照片、行程和笔记不属于 Skill 分发内容。
