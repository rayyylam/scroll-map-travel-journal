#!/usr/bin/env python3
"""Copy the bundled neutral template to a new project; Python standard library only."""
import argparse
from html import escape
from pathlib import Path
import shutil
import uuid


def create(output, title='我的旅行', dates=''):
    skill = Path(__file__).resolve().parents[1]
    source = skill / 'assets' / 'template'
    output = Path(output).expanduser().resolve()
    if output == skill or skill in output.parents:
        raise ValueError('输出目录必须位于 skill 目录之外。')
    if output.exists():
        raise ValueError('输出目录已存在，拒绝覆盖。请指定新目录，或直接修改已有作品。')
    files = [p for p in source.rglob('*') if p.is_file() and not any(
        part.startswith('.') or part == '__MACOSX' for part in p.relative_to(source).parts)]
    if not (source / 'index.html').is_file():
        raise ValueError('skill 缺少内置模板 index.html。')
    if any(p.is_symlink() or source.resolve() not in p.resolve().parents for p in files):
        raise ValueError('模板中存在符号链接或越界文件，拒绝复制。')
    output.mkdir(parents=True, exist_ok=False)
    for path in files:
        target = output / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    # Empty asset directories need not exist in the skill ZIP.
    (output / 'photos').mkdir(exist_ok=True)
    (output / 'map-art').mkdir(exist_ok=True)
    placeholder = output / 'assets' / 'photo-placeholder.svg'
    if placeholder.is_file():
        svg = placeholder.read_text(encoding='utf-8')
        placeholder.write_text(svg.replace('>我的旅行</text>', '>' + escape(title) + '</text>'), encoding='utf-8')
    html_file = output / 'index.html'
    html = html_file.read_text(encoding='utf-8')
    html = html.replace('scroll-map-journal-neutral-v1:', 'scroll-map-journal-' + uuid.uuid4().hex + ':')
    html = html.replace('<small id="trip-dates"></small>', '<small id="trip-dates">' + escape(dates) + '</small>')
    html_file.write_text(html, encoding='utf-8')
    (output / '打开与保存.md').write_text('''# 打开与保存

电脑双击项目文件夹里的 index.html 打开；如果领取的是 ZIP，先完整解压。当前是结构模板，地点、路线、章节和地图插画由制作 AI 按你的行程完成。

1. 照片先复制到 photos 文件夹，再点网页右下角「编辑」添加。选择照片只引用文件名，不会自动复制文件；双击打开时不能自动扫描新照片，请用「从电脑选择照片」。列表只展示已登记的旅行照片，不含占位图或地图插画。
2. 点文字可以编辑；可替换封面，添加/替换/删除正文照片，添加便签并在章节内排序。「完成」只退出编辑，不会导出文件；需要保存到文件请点「保存」。
3. 点「保存」下载新 index.html。先备份整个文件夹，再把下载的文件放回原文件夹替换旧 index.html；如文件名带 (1)，先改回 index.html。
4. 关闭旧页面，重新打开文件夹里的 index.html 检查。浏览器草稿不能代替文件保存。
5. 本地使用完整文件夹即可，无需额外压缩。如果需要分享或打包，跟制作 AI 说就可以。分享时 AI 会问是否包含原图，生成含全部运行素材的 ZIP；朋友在电脑上完整解压后打开 index.html，不能只发 HTML。
6. 通用占位图在 assets/，地点插画在 map-art/，也要一起保留。当前制作进度和下一步见「下一步.md」。制作 AI 应在交付时同步更新本文件开头的状态。
''', encoding='utf-8')
    (output / '下一步.md').write_text('''# 这份手账还在制作中

当前只是结构模板，不是完成品。先与制作 AI 确认主要地图点与章节安排；只需回复“按推荐做”，或说明想增加/合并哪些点。

路线初版确认后，下一步是制作地图地点插画：先完成两个代表地点的样稿并放回地图，再完成其余确认需要插画的地点。地点插画接入后检查景物、标签和载具比例，再提供一次可选背景美化，之后继续照片与笔记。右侧照片可以之后补，不影响左侧地图精修。

请把下面这句话发给正在制作的 AI：

> 请根据已确认的地图点，继续完成地点插画。先告诉我需要生成哪些图，并实际制作两个代表地点的样稿。如果当前工具不能生图，请给我逐张完整提示词、参考图和文件名，等我交回图片后继续接入。

制作 AI 应在每次阶段交付时更新此文件，写明已完成内容、还缺哪些插画以及用户此刻要做什么；全部完成后明确写“地图插画已接入”，不要继续保留本段初始说明。
''', encoding='utf-8')
    print('已创建通用结构模板：' + str(output))
    print('下一步：根据用户行程适配地图与章节，并完成地点插画。')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='新的输出目录，不覆盖已有目录')
    parser.add_argument('--title', default='我的旅行', help='唯一通用照片占位图上的旅行标题')
    parser.add_argument('--dates', default='', help='用户提供的整个行程日期范围，固定显示于地图左下角')
    args = parser.parse_args()
    try:
        create(args.output, args.title, args.dates)
    except (ValueError, OSError) as exc:
        parser.exit(1, str(exc) + '\n')
