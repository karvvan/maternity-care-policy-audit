# -*- coding: utf-8 -*-
"""
디자인 에셋 생성 (PIL) — 화이트 테마

순백 배경 위에 얹는 요소들:
  · 광택 3D 구체·링 (바닥 그림자 포함 → 원근감)
  · 반투명 그라데이션 블롭 (부드러운 배경 장식)
  · 삽화 요소: 한국 시군구 지도 실루엣, 플랫 아이콘(핀·의료 십자·차트)
  · 코랄-앰버 글로우 바
모두 RGBA PNG로 캐시 폴더에 저장.
"""
import os, math, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CACHE = os.environ.get('ASSET_DIR') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '_assets')
os.makedirs(CACHE, exist_ok=True)
def _project_root(start):
    """04_제출물 폴더가 있는 상위 디렉터리를 프로젝트 루트로 본다 (스크립트 위치에 무관)"""
    d = os.path.dirname(os.path.abspath(start))
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, '04_제출물')):
            return d
        d = os.path.dirname(d)
    raise RuntimeError('프로젝트 루트를 찾지 못했습니다')


BASE = _project_root(__file__)


def _cached(name):
    return os.path.join(CACHE, f'{name}.png')


# ── 3D 구체 ─────────────────────────────────────────────────
def sphere(name, size=420, color=(255, 122, 89), color2=None):
    path = _cached(name)
    if os.path.exists(path):
        return path
    s = size
    pad = int(s * 0.25)
    W = s + pad * 2
    im = Image.new('RGBA', (W, W + pad), (0, 0, 0, 0))
    sh = Image.new('RGBA', (W, W + pad), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([pad + s * 0.06, pad + s * 0.94, pad + s * 0.94, pad + s * 1.13],
                               fill=(30, 45, 70, 88))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(s * 0.05)))
    c1 = np.array(color, np.float32)
    c2 = np.array(color2 if color2 else [max(0, c - 130) for c in color], np.float32)
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    cx, cy = s * 0.36, s * 0.32
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (s * 0.85)
    t = np.clip(d, 0, 1)[..., None]
    body = (c1[None, None, :] * (1 - t) + c2[None, None, :] * t).astype(np.uint8)
    mask = ((xx - s / 2) ** 2 + (yy - s / 2) ** 2 <= (s / 2) ** 2).astype(np.uint8) * 255
    ball = Image.fromarray(np.dstack([body, mask]), 'RGBA')
    hi = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(hi).ellipse([s * 0.22, s * 0.13, s * 0.46, 0.32 * s], fill=(255, 255, 255, 175))
    ball = Image.alpha_composite(ball, hi.filter(ImageFilter.GaussianBlur(s * 0.035)))
    im.alpha_composite(ball, (pad, pad))
    im.save(path)
    return path


# ── 3D 링 ───────────────────────────────────────────────────
def ring(name, size=460, color=(108, 158, 255), thick=0.16, tilt=0.42):
    path = _cached(name)
    if os.path.exists(path):
        return path
    S = size * 3
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    n = 720
    rw = S * 0.42
    rh = rw * tilt
    cx = cy = S / 2
    tk = S * thick / 2
    c = np.array(color, np.float32)
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = cx + rw * math.cos(a), cy + rh * math.sin(a)
        lum = 0.55 + 0.45 * (-math.sin(a) * 0.5 + 0.5)
        col = tuple(int(v) for v in np.clip(c * lum + 40 * (lum - .55), 0, 255)) + (235,)
        r = tk * (0.82 + 0.18 * math.cos(a - 0.7))
        dr.ellipse([x - r, y - r, x + r, y + r], fill=col)
    im = im.resize((size, size), Image.LANCZOS)
    sh = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([size * .16, size * .74, size * .88, size * .94], fill=(30, 45, 70, 70))
    out = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(size * 0.035)), im)
    out.save(path)
    return path


# ── 반투명 그라데이션 블롭 ──────────────────────────────────
def blob(name, size=900, c1=(255, 122, 89), c2=(255, 184, 107), peak=110):
    """중심 c1 → 가장자리 투명. 흰 배경 장식용 (낮은 알파)."""
    path = _cached(name)
    if os.path.exists(path):
        return path
    s = size
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    d = np.sqrt((xx - s / 2) ** 2 + (yy - s / 2) ** 2) / (s / 2)
    t = np.clip(d, 0, 1)
    col = (np.array(c1, np.float32)[None, None, :] * (1 - t[..., None])
           + np.array(c2, np.float32)[None, None, :] * t[..., None])
    alpha = (np.exp(-(d ** 2) * 2.6) * peak).astype(np.uint8)
    img = np.dstack([col.astype(np.uint8), alpha])
    Image.fromarray(img, 'RGBA').save(path)
    return path


# ── 글로우 바 ───────────────────────────────────────────────
def glow_bar(name, w=1200, h=14, c1=(255, 122, 89), c2=(255, 184, 107)):
    path = _cached(name)
    if os.path.exists(path):
        return path
    x = np.linspace(0, 1, w, dtype=np.float32)[None, :, None]
    col = np.array(c1, np.float32)[None, None, :] * (1 - x) + np.array(c2, np.float32)[None, None, :] * x
    col = np.repeat(col, h, axis=0)
    alpha = (np.sin(np.linspace(0, math.pi, w)) ** 0.5 * 255)[None, :, None]
    alpha = np.repeat(alpha, h, axis=0)
    Image.fromarray(np.dstack([col, alpha]).astype(np.uint8), 'RGBA').save(path)
    return path


# ── 삽화: 한국 지도 실루엣 ──────────────────────────────────
def korea_map(name='korea_map', size=1400, fill=(27, 48, 80, 255), line=(255, 255, 255, 60)):
    path = _cached(name)
    if os.path.exists(path):
        return path
    geo = os.path.join(BASE, '02_데이터', 'skorea-municipalities-2018-geo.json')
    gj = json.load(open(geo, encoding='utf-8'))
    lon0, lon1, lat0, lat1 = 125.0, 130.0, 33.0, 38.7
    W = size
    H = int(size * (lat1 - lat0) / (lon1 - lon0) * 1.23)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)

    def tr(lon, lat):
        return ((lon - lon0) / (lon1 - lon0) * W, (1 - (lat - lat0) / (lat1 - lat0)) * H)

    def rings(geom):
        return [geom['coordinates'][0]] if geom['type'] == 'Polygon' else [p[0] for p in geom['coordinates']]

    for f in gj['features']:
        for r in rings(f['geometry']):
            pts = [tr(x, y) for x, y in r]
            if len(pts) >= 3:
                dr.polygon(pts, fill=fill, outline=line)
    # 그림자
    sh = Image.new('RGBA', (W + 60, H + 60), (0, 0, 0, 0))
    mask = im.split()[3].point(lambda a: min(a, 70))
    shadow_layer = Image.new('RGBA', im.size, (30, 45, 70, 255))
    sh.paste(shadow_layer, (26, 34), mask)
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    out = Image.new('RGBA', (W + 60, H + 60), (0, 0, 0, 0))
    out = Image.alpha_composite(out, sh)
    out.alpha_composite(im, (0, 0))
    out.save(path)
    return path


# ── 삽화: 플랫 아이콘 (그림자 포함) ─────────────────────────
def _icon_canvas(s):
    im = Image.new('RGBA', (s, int(s * 1.12)), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def _icon_shadow(im, s):
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([s * 0.18, s * 0.96, s * 0.82, s * 1.08], fill=(30, 45, 70, 80))
    return Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(s * 0.04)), im)


def icon_pin(name='icon_pin', size=360, c1=(255, 110, 80), c2=(255, 170, 100)):
    path = _cached(name)
    if os.path.exists(path):
        return path
    s = size
    im, dr = _icon_canvas(s)
    # 물방울 핀: 원 + 삼각
    grad = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for i in range(s):
        t = i / s
        col = tuple(int(a * (1 - t) + b * t) for a, b in zip(c1, c2)) + (255,)
        gd.line([(0, i), (s, i)], fill=col)
    mask = Image.new('L', (s, s), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([s * 0.18, s * 0.05, s * 0.82, s * 0.69], fill=255)
    md.polygon([(s * 0.26, s * 0.52), (s * 0.74, s * 0.52), (s * 0.5, s * 0.95)], fill=255)
    im.paste(grad, (0, 0), mask)
    dr.ellipse([s * 0.38, s * 0.24, s * 0.62, s * 0.48], fill=(255, 255, 255, 235))
    im = _icon_shadow(im, s)
    im.save(path)
    return path


def icon_med(name='icon_med', size=360, base=(94, 210, 190)):
    path = _cached(name)
    if os.path.exists(path):
        return path
    s = size
    im, dr = _icon_canvas(s)
    r = s * 0.16
    dr.rounded_rectangle([s * 0.12, s * 0.12, s * 0.88, s * 0.88], radius=r,
                         fill=base + (255,))
    hi = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi).rounded_rectangle([s * 0.12, s * 0.12, s * 0.88, s * 0.5], radius=r,
                                         fill=(255, 255, 255, 55))
    im = Image.alpha_composite(im, hi)
    dr = ImageDraw.Draw(im)
    w = s * 0.11
    dr.rounded_rectangle([s * 0.5 - w, s * 0.28, s * 0.5 + w, s * 0.72], radius=w * 0.5,
                         fill=(255, 255, 255, 245))
    dr.rounded_rectangle([s * 0.28, s * 0.5 - w, s * 0.72, s * 0.5 + w], radius=w * 0.5,
                         fill=(255, 255, 255, 245))
    im = _icon_shadow(im, s)
    im.save(path)
    return path


def icon_chart(name='icon_chart', size=360, base=(96, 140, 255)):
    path = _cached(name)
    if os.path.exists(path):
        return path
    s = size
    im, dr = _icon_canvas(s)
    dr.rounded_rectangle([s * 0.1, s * 0.1, s * 0.9, s * 0.9], radius=s * 0.15,
                         fill=(240, 245, 252, 255), outline=(200, 212, 228, 255), width=3)
    bars = [(0.24, 0.52), (0.45, 0.36), (0.66, 0.22)]
    for i, (x, top) in enumerate(bars):
        col = base if i < 2 else (255, 122, 89)
        dr.rounded_rectangle([s * x, s * top, s * (x + 0.13), s * 0.78], radius=s * 0.035,
                             fill=col + (255,))
    im = _icon_shadow(im, s)
    im.save(path)
    return path


def build_defaults():
    return {
        'sphere_coral': sphere('sphere_coral', 420, (255, 138, 101), (150, 40, 34)),
        'sphere_blue': sphere('sphere_blue', 300, (120, 168, 255), (30, 50, 130)),
        'sphere_teal': sphere('sphere_teal', 210, (110, 231, 210), (12, 96, 100)),
        'ring_blue': ring('ring_blue', 520, (108, 158, 255)),
        'ring_coral': ring('ring_coral', 380, (255, 150, 110)),
        'glow_bar': glow_bar('glow_bar'),
        'blob_coral': blob('blob_coral', 900, (255, 140, 105), (255, 200, 150), 70),
        'blob_blue': blob('blob_blue', 1000, (120, 168, 255), (170, 205, 255), 60),
        'blob_teal': blob('blob_teal', 700, (110, 231, 210), (180, 245, 232), 55),
        'korea_map': korea_map(),
        'icon_pin': icon_pin(),
        'icon_med': icon_med(),
        'icon_chart': icon_chart(),
    }


if __name__ == '__main__':
    import io, sys
    if (sys.stdout.encoding or '').lower() not in ('utf-8', 'utf8'):   # 중복 래핑 방지
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    for k, v in build_defaults().items():
        print(k, '->', os.path.basename(v))
