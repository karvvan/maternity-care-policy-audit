# -*- coding: utf-8 -*-
"""
PPT·영상용 디자인 에셋 생성 (PIL)

다크 '오로라' 테마: 딥네이비 그라데이션 배경 + 블러 컬러 블롭 + 도트 그리드,
3D 구체·링 조형물(하이라이트·그림자 포함). 생성물은 캐시 폴더에 PNG(RGBA)로 저장.
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CACHE = os.environ.get('ASSET_DIR') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '_assets')
os.makedirs(CACHE, exist_ok=True)


def _radial_blob(w, h, cx, cy, radius, color, peak):
    """additive 블러 블롭 레이어 (float array h×w×3)"""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d2 = ((x - cx) ** 2 + (y - cy) ** 2) / (radius ** 2)
    fall = np.exp(-d2 * 2.2) * peak
    layer = np.zeros((h, w, 3), np.float32)
    for i in range(3):
        layer[:, :, i] = fall * color[i]
    return layer


def bg_dark(name, w=1920, h=1080, blobs=None, grid=True):
    """딥네이비 배경 + 블롭 + 도트 그리드 + 비네트 + 노이즈"""
    path = os.path.join(CACHE, f'{name}.png')
    if os.path.exists(path):
        return path
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    x = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    top, bot = np.array([11, 18, 32], np.float32), np.array([16, 27, 48], np.float32)
    grad = top[None, None, :] * (1 - y[..., None]) + bot[None, None, :] * y[..., None]
    img = np.broadcast_to(grad, (h, w, 3)).copy()
    img += x[..., None] * 10 + y[..., None] * 6  # 미세한 대각 밝기
    if blobs is None:
        blobs = [(0.86, 0.12, 620, (255, 122, 89), 34),   # 코랄 (우상)
                 (0.10, 0.92, 700, (78, 110, 200), 42),   # 블루 (좌하)
                 (0.32, 0.18, 420, (94, 234, 212), 14)]   # 틸 (좌상, 은은)
    for bx, by, r, c, p in blobs:
        img += _radial_blob(w, h, bx * w, by * h, r, np.array(c, np.float32) / 255.0, p)
    # 비네트
    d = np.sqrt(((x - .5) * 1.15) ** 2 + ((y - .5) * 1.0) ** 2)
    img *= (1 - 0.35 * np.clip(d - .35, 0, 1))[..., None]
    # 노이즈
    rng = np.random.default_rng(7)
    img += rng.normal(0, 1.6, (h, w, 1))
    img = np.clip(img, 0, 255).astype(np.uint8)
    im = Image.fromarray(img, 'RGB')
    if grid:
        g = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        dr = ImageDraw.Draw(g)
        for gx in range(60, w, 56):
            for gy in range(60, h, 56):
                dr.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=(255, 255, 255, 9))
        im = Image.alpha_composite(im.convert('RGBA'), g).convert('RGB')
    im.save(path)
    return path


def sphere(name, size=420, color=(255, 122, 89), color2=None):
    """광택 3D 구체 + 바닥 그림자 (RGBA)"""
    path = os.path.join(CACHE, f'{name}.png')
    if os.path.exists(path):
        return path
    s = size
    pad = int(s * 0.25)
    W = s + pad * 2
    im = Image.new('RGBA', (W, W + pad), (0, 0, 0, 0))
    # 바닥 그림자
    sh = Image.new('RGBA', (W, W + pad), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([pad + s * 0.08, pad + s * 0.92, pad + s * 0.92, pad + s * 1.12],
                               fill=(0, 0, 0, 110))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(s * 0.045)))
    # 본체: 좌상 광원 라디얼 그라데이션
    c1 = np.array(color, np.float32)
    c2 = np.array(color2 if color2 else [max(0, c - 130) for c in color], np.float32)
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    cx, cy = s * 0.36, s * 0.32
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (s * 0.85)
    t = np.clip(d, 0, 1)[..., None]
    body = (c1[None, None, :] * (1 - t) + c2[None, None, :] * t).astype(np.uint8)
    mask = ((xx - s / 2) ** 2 + (yy - s / 2) ** 2 <= (s / 2) ** 2).astype(np.uint8) * 255
    ball = Image.fromarray(np.dstack([body, mask]), 'RGBA')
    # 스펙큘러 하이라이트
    hi = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(hi).ellipse([s * 0.22, s * 0.13, s * 0.46, 0.32 * s], fill=(255, 255, 255, 165))
    ball = Image.alpha_composite(ball, hi.filter(ImageFilter.GaussianBlur(s * 0.035)))
    im.alpha_composite(ball, (pad, pad))
    im.save(path)
    return path


def ring(name, size=460, color=(108, 158, 255), thick=0.16, tilt=0.42):
    """기울어진 3D 링 (RGBA)"""
    path = os.path.join(CACHE, f'{name}.png')
    if os.path.exists(path):
        return path
    S = size * 3  # 슈퍼샘플
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
        # 위쪽(광원 방향) 밝게
        lum = 0.55 + 0.45 * (-math.sin(a) * 0.5 + 0.5)
        col = tuple(int(v) for v in np.clip(c * lum + 40 * (lum - .55), 0, 255)) + (235,)
        r = tk * (0.82 + 0.18 * math.cos(a - 0.7))
        dr.ellipse([x - r, y - r, x + r, y + r], fill=col)
    im = im.resize((size, size), Image.LANCZOS)
    sh = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([size * .18, size * .72, size * .86, size * .92], fill=(0, 0, 0, 90))
    out = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(size * 0.03)), im)
    out.save(path)
    return path


def glow_bar(name, w=1200, h=14, c1=(255, 122, 89), c2=(255, 184, 107)):
    """양끝이 사라지는 그라데이션 액센트 바 (RGBA)"""
    path = os.path.join(CACHE, f'{name}.png')
    if os.path.exists(path):
        return path
    x = np.linspace(0, 1, w, dtype=np.float32)[None, :, None]
    col = np.array(c1, np.float32)[None, None, :] * (1 - x) + np.array(c2, np.float32)[None, None, :] * x
    col = np.repeat(col, h, axis=0)
    alpha = (np.sin(np.linspace(0, math.pi, w)) ** 0.5 * 255)[None, :, None]
    alpha = np.repeat(alpha, h, axis=0)
    img = np.dstack([col, alpha]).astype(np.uint8)
    Image.fromarray(img, 'RGBA').save(path)
    return path


def build_defaults():
    out = {
        'bg_main': bg_dark('bg_main'),
        'bg_title': bg_dark('bg_title', blobs=[(0.78, 0.24, 780, (255, 122, 89), 46),
                                               (0.12, 0.86, 860, (78, 110, 200), 52),
                                               (0.45, 0.05, 500, (94, 234, 212), 18)]),
        'bg_closing': bg_dark('bg_closing', blobs=[(0.5, 0.1, 900, (78, 110, 200), 40),
                                                   (0.85, 0.85, 700, (255, 122, 89), 36)]),
        'sphere_coral': sphere('sphere_coral', 420, (255, 138, 101), (140, 34, 30)),
        'sphere_blue': sphere('sphere_blue', 300, (120, 168, 255), (24, 40, 110)),
        'sphere_teal': sphere('sphere_teal', 210, (110, 231, 210), (10, 80, 84)),
        'ring_blue': ring('ring_blue', 520, (108, 158, 255)),
        'ring_coral': ring('ring_coral', 380, (255, 150, 110)),
        'glow_bar': glow_bar('glow_bar'),
    }
    return out


if __name__ == '__main__':
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    for k, v in build_defaults().items():
        print(k, '->', v)
