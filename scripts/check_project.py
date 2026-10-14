#!/usr/bin/env python3
"""Check static project dependencies and structure; does not validate browser behavior."""
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.resources, self.anchors, self.css = [], [], [], []
        self.style_depth = 0
        self.css_files = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.append(a['id'])
        if tag == 'style':
            self.style_depth += 1
        if a.get('style'):
            self.css.append(a['style'])
        if tag == 'a' and a.get('href', '').startswith('#'):
            self.anchors.append(a['href'][1:])
        for attr in ('src', 'poster'):
            if a.get(attr):
                self.resources.append(a[attr])
        if tag in ('image', 'use', 'link'):
            value = a.get('href') or a.get('xlink:href')
            if value:
                self.resources.append(value)
                if tag == 'link' and a.get('rel') == 'stylesheet':
                    self.css_files.append(value)

    def handle_endtag(self, tag):
        if tag == 'style':
            self.style_depth = max(0, self.style_depth - 1)

    def handle_data(self, data):
        if self.style_depth:
            self.css.append(data)


def inspect(project, stage='draft', accept_vector=False):
    root = Path(project).expanduser().resolve()
    errors, warnings, incomplete = [], [], []
    if not (root / 'index.html').is_file():
        return {'errors': ['缺少 index.html'], 'warnings': [], 'status': 'failed'}
    html = (root / 'index.html').read_text(encoding='utf-8')
    page = Page()
    page.feed(html)
    for value, count in Counter(page.ids).items():
        if count > 1:
            errors.append('重复 ID：' + value)
    for anchor in page.anchors:
        if anchor and anchor not in page.ids:
            errors.append('无效章节锚点：#' + anchor)
    for element in ('journey', 'hero'):
        if element not in page.ids:
            errors.append('缺少模板结构 ID：' + element)

    def local_path(value, base):
        url = urlsplit(value)
        if value.startswith('#'):
            return None
        if url.scheme in ('http', 'https') or url.netloc:
            warnings.append('远程运行依赖：' + value)
            return None
        if url.scheme in ('data', 'blob'):
            warnings.append('内嵌或临时资源，请检查可保存性与来源：' + value[:65])
            return None
        if url.scheme or value.startswith(('/', '\\')) or re.match(r'^[A-Za-z]:', value):
            errors.append('非便携资源路径：' + value)
            return None
        target = (base / unquote(url.path)).resolve()
        if root != target and root not in target.parents:
            errors.append('资源越过项目目录：' + value)
        elif not target.is_file():
            errors.append('资源文件缺失：' + value)
        else:
            return target
        return None

    for value in page.resources:
        local_path(value, root)
    css_blobs = [(css, root) for css in page.css]
    for value in page.css_files:
        path = local_path(value, root)
        if path:
            css_blobs.append((path.read_text(encoding='utf-8'), path.parent))
    for css, base in css_blobs:
        for match in re.finditer(r'url\(\s*[\'"]?([^\)\'"\s]+)', css):
            local_path(match.group(1), base)
    # Literal image paths also cover the template's JS art configuration.
    for value in re.findall(r'[\'"]((?:photos|map-art|assets)/[^\'"\n]+\.(?:png|webp|jpg|jpeg|gif|svg))[\'"]', html, re.I):
        local_path(value, root)
    for directory in ('photos', 'fonts', 'vendor', 'licenses'):
        if not (root / directory).is_dir():
            errors.append('缺少目录：' + directory)
    if '示例' in html or 'photo-placeholder.svg' in html:
        warnings.append('仍有模板示例或占位素材，请确认当前交付阶段。')
    placeholders = []
    for folder in ('photos', 'assets'):
        for path in (root / folder).rglob('*'):
            if path.is_file() and re.match(r'^(?:photo-placeholder|placeholder(?:[-_.]|$)|sample-(?:sea|island|note)\.svg$)', path.name, re.I):
                placeholders.append(path.relative_to(root).as_posix())
    if len(placeholders) > 1:
        incomplete.append('占位图超过一张：复用 assets/photo-placeholder.svg，不按地点分别生成。')
    if any(p.startswith('photos/') for p in placeholders):
        incomplete.append('照片目录混入占位图：通用占位图应放在 assets/，不进入选图列表。')

    map_stats = {'places': None, 'required_art': None, 'missing_art': []}
    match = re.search(r'\bconst\s+MAP_PLACES\s*=\s*', html)
    try:
        places = json.JSONDecoder().raw_decode(html[match.end():])[0] if match else None
        if not isinstance(places, list) or not all(isinstance(p, dict) for p in places):
            raise ValueError('MAP_PLACES 必须为 JSON 数组')
        required = [p for p in places if p.get('art_required', p.get('kind') == 'main')]
        map_stats.update(places=len(places), required_art=len(required))
        for place in places:
            art = place.get('art')
            if art:
                if not isinstance(art, list) or len(art) != 5 or not isinstance(art[0], str):
                    errors.append('地点插画配置格式错误：' + str(place.get('id', '?')))
                    continue
                local_path(art[0], root)
        if not accept_vector:
            for place in required:
                art = place.get('art')
                label = str(place.get('name') or place.get('id') or '?')
                if not isinstance(art, list) or not art or not isinstance(art[0], str) or not re.search(r'\.(?:png|webp|jpe?g)$', art[0], re.I):
                    map_stats['missing_art'].append(label)
            if map_stats['missing_art']:
                incomplete.append('地图插画待制作或接入：' + '、'.join(map_stats['missing_art']))
            if not required and not any(p.get('art') for p in places):
                incomplete.append('地图未声明需插画的地点且没有插画，请核对确认方案。')
    except (ValueError, TypeError):
        incomplete.append('无法静态核对 MAP_PLACES：保留 JSON 数组配置，或另行人工核对所有地点插画。')
    if accept_vector:
        warnings.append('本次按明确接受的矢量风格检查；需在制作记录中保留用户选择，不能称为已完成生图。')
    if stage == 'final':
        errors.extend(incomplete)
    else:
        warnings.extend(incomplete)
    return {'status': 'failed' if errors else 'static-check-passed',
            'stage': stage, 'completion': 'needs-work' if errors or incomplete else 'requires-visual-review',
            'map': map_stats, 'placeholder_files': placeholders,
            'errors': sorted(set(errors)), 'warnings': sorted(set(warnings)),
            'next_action': '继续完成缺失插画并告知用户具体下一步；照片可后补。' if map_stats['missing_art'] else '核对以上问题并进行浏览器验收。',
            'note': '只检查静态结构与显式资源；地图美术、动态脚本引用、滚动和保存重开仍需浏览器验证。'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project')
    parser.add_argument('--stage', choices=('draft', 'final'), default='draft', help='final 会把缺失地点插画、多张占位图作为未完成项')
    parser.add_argument('--accept-vector', action='store_true', help='仅当用户明确选择矢量风格时使用，并记录其选择')
    args = parser.parse_args()
    try:
        report = inspect(args.project, args.stage, args.accept_vector)
    except (OSError, ValueError) as exc:
        report = {'status': 'failed', 'errors': [str(exc)], 'warnings': []}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(1 if report['errors'] else 0)
