# -*- coding: utf-8 -*-
"""
시연 영상용 모션그래픽 소스 생성 — 화이트 테마
(나레이션 없음: 대표자가 직접 녹음해 얹는 용도)

순백 배경 + 떠 있는 카드(소프트 섀도) + 반투명 블롭 장식.
보고서 핵심 내용을 파트별 클립(mp4, 1920x1080/30fps)으로 렌더링한다.

사용법:
  python 영상소스_생성.py            # 전체 렌더
  python 영상소스_생성.py 3-1 5-4    # 지정 클립만
출력: 04_제출물/영상소스/<번호>_<이름>.mp4
"""
import os, sys, io, json, math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Polygon as MplPolygon, Wedge, Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.animation import FuncAnimation, FFMpegWriter
from PIL import Image

import design_assets

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, '04_제출물', '영상소스')
os.makedirs(OUT, exist_ok=True)
ASSETS = design_assets.build_defaults()

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

FPS = 30
# 화이트 테마 팔레트
TXT, MUT = '#22303F', '#6A7B92'
ACC = '#FF7A59'          # 코랄 (도형)
ACC_T = '#E8654A'        # 코랄 (텍스트)
AMB = '#E8882E'          # 앰버 (텍스트 강조)
BLU = '#4A78C2'
TEA = '#149E8C'
DANGER = '#E8654A'
NAVY = '#1B3A5F'
TRACK = '#E9EEF5'        # 게이지 트랙·빈 영역
CARD_EDGE = '#E4EAF2'

# 배경: 순백 + 은은한 블롭
_bg_path = os.path.join(design_assets.CACHE, 'bg_motion_white.png')
if not os.path.exists(_bg_path):
    cv = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))
    b1 = Image.open(ASSETS['blob_blue']).resize((1250, 1250))
    b2 = Image.open(ASSETS['blob_coral']).resize((1150, 1150))
    cv.alpha_composite(b1, (-520, 480))
    cv.alpha_composite(b2, (1180, -520))
    cv.convert('RGB').save(_bg_path)
BG_IMG = np.asarray(Image.open(_bg_path).convert('RGB')) / 255.0

CLIPS = {}


def clip(cid, title, dur):
    def deco(fn):
        CLIPS[cid] = (title, dur, fn)
        return fn
    return deco


# ── 공통 유틸 ───────────────────────────────────────────────
def ease(t):
    t = min(max(t, 0), 1)
    return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2


def eout(t):
    t = min(max(t, 0), 1)
    return 1 - (1 - t) ** 3


def seg(t, a, b):
    if b <= a:
        return 1.0
    return min(max((t - a) / (b - a), 0), 1)


def canvas():
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 192)
    ax.set_ylim(0, 108)
    ax.axis('off')
    ax.imshow(BG_IMG, extent=[0, 192, 0, 108], aspect='auto', zorder=0)
    return fig, ax


def title_bar(ax, text, sub=None, alpha=1.0):
    ax.add_patch(Circle((10, 98), 1.5, facecolor=ACC, edgecolor='none', alpha=alpha, zorder=5))
    ax.text(14, 98, text, fontsize=27, fontweight='bold', color=TXT, va='center', alpha=alpha, zorder=5)
    if sub:
        ax.text(14, 92.6, sub, fontsize=15, color=MUT, va='center', alpha=alpha, zorder=5)


def card_box(ax, x, y, w, h, alpha=1.0, fc='#FFFFFF', ec=CARD_EDGE, lw=1.2, z=3, warn=False):
    """떠 있는 카드: 이중 소프트 섀도 + 흰 면"""
    if warn:
        fc, ec = '#FFF3EE', '#F6CDBE'
    for off, sa in [(1.4, 0.10), (0.7, 0.13)]:
        ax.add_patch(FancyBboxPatch((x + off * 0.35, y - off * 0.5), w, h,
                                    boxstyle='round,pad=0.6,rounding_size=1.6',
                                    facecolor=(0.16, 0.24, 0.38, sa * alpha), edgecolor='none',
                                    zorder=z - 0.1))
    p = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.6,rounding_size=1.6',
                       facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z, alpha=alpha)
    ax.add_patch(p)
    return p


def render(cid):
    title, dur, fn = CLIPS[cid]
    frames = int(dur * FPS)
    fig, ax = canvas()
    state = {}

    def update(i):
        for a in list(ax.patches) + list(ax.texts) + list(ax.lines) + list(ax.collections):
            a.remove()
        fn(ax, i / (frames - 1), i / FPS, state)

    anim = FuncAnimation(fig, update, frames=frames, interval=1000 / FPS)
    path = os.path.join(OUT, f'{cid}_{title}.mp4')
    anim.save(path, writer=FFMpegWriter(fps=FPS, codec='libx264',
                                        extra_args=['-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium']))
    plt.close(fig)
    print(f'  {cid} {title} ({dur}s) → {os.path.basename(path)}')


# ═══ PART 1 · 문제와 제도 ═══════════════════════════════════
@clip('1-1', '파이프라인_빌드업', 9)
def c11(ax, t, sec, st):
    title_bar(ax, '취약지 정책은 세 단계 파이프라인이다')
    nodes = [('① 측정', '2년마다 접근성·이용률 산출', 18, TEA, 0.05),
             ('② 지정', '이동시간 지표만으로 판정', 76, ACC, 0.30),
             ('③ 배분', '줄 세우는 규칙이 없음', 134, DANGER, 0.55)]
    for name, desc, x, color, t0 in nodes:
        a = ease(seg(t, t0, t0 + 0.18))
        if a <= 0:
            continue
        y = 48 + (1 - a) * 6
        card_box(ax, x, y, 40, 22, alpha=a)
        ax.add_patch(Rectangle((x, y + 20.6), 40 * a, 1.4, facecolor=color, edgecolor='none',
                               alpha=a, zorder=4))
        ax.text(x + 20, y + 14.5, name, fontsize=23, fontweight='bold', color=TXT,
                ha='center', alpha=a, zorder=5)
        ax.text(x + 20, y + 7, desc, fontsize=13.5, color=MUT, ha='center', alpha=a, zorder=5)
    for xa, t0 in [(60.5, 0.24), (118.5, 0.49)]:
        a = ease(seg(t, t0, t0 + 0.1))
        if a > 0:
            ax.annotate('', xy=(xa + 12 * a, 59), xytext=(xa, 59),
                        arrowprops=dict(arrowstyle='-|>', color=MUT, lw=3, alpha=a), zorder=4)
    if t > 0.78:
        pulse = 0.5 + 0.5 * math.sin(sec * 5)
        for x in (96, 154):
            ax.add_patch(Circle((x, 72.5), 2.2 + pulse * 0.9, facecolor='none',
                                edgecolor=DANGER, lw=2.5, alpha=0.75 - pulse * 0.35, zorder=6))
            ax.text(x, 72.5, '?', fontsize=17, fontweight='bold', color=DANGER,
                    ha='center', va='center', zorder=7)
    a = ease(seg(t, 0.82, 0.95))
    if a > 0:
        ax.text(96, 30, '측정은 정밀하다 — 그런데 지정과 배분은 그 측정을 따르는가?',
                fontsize=19, fontweight='bold', color=TXT, ha='center', alpha=a, zorder=5)


@clip('1-2', '취약도_배점_0점', 8)
def c12(ax, t, sec, st):
    title_bar(ax, '지원 심사 배점 100점, 취약도 항목은?')
    cx, cy, r = 60, 52, 26
    a1 = ease(seg(t, 0.08, 0.5))
    ax.add_patch(Wedge((cx, cy), r, 0, 360, width=8, facecolor=TRACK, edgecolor='none', zorder=3))
    for start, span, color in [(90, -72 * a1, BLU), (90 - 72 * a1, -288 * a1, '#8FA8CE')]:
        if abs(span) > 1:
            ax.add_patch(Wedge((cx, cy), r, min(start, start + span), max(start, start + span),
                               width=8, facecolor=color, edgecolor='none', zorder=4))
    ax.text(cx, cy + 3, '심사 100점', fontsize=17, color=MUT, ha='center', zorder=5)
    n0 = int((1 - ease(seg(t, 0.45, 0.8))) * 100) if t > 0.45 else 100
    ax.text(cx, cy - 6, f'취약도 {n0}점' if t > 0.45 else '취약도 ?점', fontsize=25, fontweight='bold',
            color=DANGER if t > 0.45 else TXT, ha='center', zorder=5)
    a2 = ease(seg(t, 0.5, 0.75))
    if a2 > 0:
        card_box(ax, 104, 38, 74, 30, alpha=a2, warn=True)
        ax.text(141, 59, '취약도 항목 0점', fontsize=30, fontweight='bold', color=DANGER,
                ha='center', alpha=a2, zorder=5)
        ax.text(141, 49.5, '심사는 "얼마나 급한가"가 아니라', fontsize=15.5, color=TXT, ha='center', alpha=a2, zorder=5)
        ax.text(141, 44, '"얼마나 해낼 수 있는가"를 본다', fontsize=15.5, color=TXT, ha='center', alpha=a2, zorder=5)


@clip('1-3', '등급_구성_108곳', 8)
def c13(ax, t, sec, st):
    title_bar(ax, '분만취약지 등급 — A·B·C 108곳', '공고 제2026-144호')
    data = [('A', 32, ACC, '두 지표 모두 취약'), ('B', 21, '#FFB86B', '하나만 취약'),
            ('C', 55, BLU, '배경인구 미달 또는 지원 기수령')]
    total_w = 150.0
    x = 21
    for i, (g, n, color, desc) in enumerate(data):
        w = total_w * n / 108
        a = ease(seg(t, 0.08 + i * 0.22, 0.3 + i * 0.22))
        if a > 0:
            ax.add_patch(FancyBboxPatch((x, 52), w * a, 16, boxstyle='round,pad=0.4,rounding_size=1.2',
                                        facecolor=color, edgecolor='none', alpha=0.92, zorder=4))
            ax.text(x + w * a / 2, 60, f'{g} · {int(n * a)}곳', fontsize=21, fontweight='bold',
                    color='white', ha='center', va='center', zorder=5)
            ax.text(x + w / 2, 46.5, desc, fontsize=12.5, color=MUT, ha='center', alpha=a, zorder=5)
        x += w + 1.5
    a2 = ease(seg(t, 0.75, 0.92))
    if a2 > 0:
        ax.text(96, 30, 'C는 취약도 순위가 아니라 자격표 — "지원받으면 C가 된다"',
                fontsize=18.5, fontweight='bold', color=TXT, ha='center', alpha=a2, zorder=5)
        ax.text(96, 24, '이 정의 구조가 배분 분석의 설계(C 제외)를 결정한다', fontsize=14, color=MUT,
                ha='center', alpha=a2, zorder=5)


# ═══ PART 2 · 데이터 ════════════════════════════════════════
@clip('2-1', '데이터_대시보드', 8)
def c21(ax, t, sec, st):
    title_bar(ax, '전량 공개 데이터로만 분석한다', '공공데이터포털 · 복지부 공고·지침')
    cards = [('226만', '행 — 헬스맵 9종 (2023)', 0.05), ('108곳', 'A·B·C 등급표 전사', 0.2),
             ('343쪽', '정부 지침 완독·임계값 추출', 0.35), ('3종', '직접 구축 파생 데이터', 0.5)]
    for i, (num, desc, t0) in enumerate(cards):
        a = ease(seg(t, t0, t0 + 0.2))
        if a <= 0:
            continue
        x = 14 + (i % 2) * 86
        y = 52 - (i // 2) * 26 + (1 - a) * 4
        card_box(ax, x, y, 78, 20, alpha=a)
        ax.text(x + 6, y + 10, num, fontsize=30, fontweight='bold', color=AMB, va='center',
                alpha=a, zorder=5)
        ax.text(x + 32, y + 10, desc, fontsize=15, color=TXT, va='center', alpha=a, zorder=5)
    a2 = ease(seg(t, 0.78, 0.93))
    if a2 > 0:
        ax.text(96, 14, '로그인도 승인도 필요 없다 — 누구나 같은 결과를 재현할 수 있다',
                fontsize=17, fontweight='bold', color=TEA, ha='center', alpha=a2, zorder=5)


@clip('2-2', 'OD_유출_흐름', 10)
def c22(ax, t, sec, st):
    title_bar(ax, '환자 유출입 226만 행 — 누가 어디로 가서 낳는가')
    rng = np.random.default_rng(11)
    if 'pts' not in st:
        st['pts'] = rng.uniform([30, 30], [70, 72], (46, 2))
        st['dst'] = rng.uniform([128, 38], [168, 66], (46, 2))
        st['ph'] = rng.uniform(0, 1, 46)
    card_box(ax, 24, 24, 52, 54)
    card_box(ax, 122, 24, 52, 54)
    ax.text(50, 82.5, '거주지 (수요)', fontsize=16, color=MUT, ha='center', zorder=5)
    ax.text(148, 82.5, '진료지 (공급)', fontsize=16, color=MUT, ha='center', zorder=5)
    prog = ease(seg(t, 0.1, 0.85))
    for (p, d, ph) in zip(st['pts'], st['dst'], st['ph']):
        u = min((prog * 1.25 + ph) % 1.25, 1.0)
        cx = p[0] + (d[0] - p[0]) * eout(u)
        cy = p[1] + (d[1] - p[1]) * eout(u) + math.sin(u * math.pi) * 6
        ax.add_patch(Circle((cx, cy), 0.9, facecolor=ACC if u < 1 else TEA, edgecolor='none',
                            alpha=0.9, zorder=6))
    ax.add_patch(Circle((148, 51), 3.2, facecolor=TEA, edgecolor='white', lw=1.5, alpha=0.95, zorder=7))
    a2 = ease(seg(t, 0.55, 0.8))
    if a2 > 0:
        ax.text(96, 14, '유출입 행렬을 기관 소재지 기준으로 합산 → "관내 분만 수행량" 직접 구축 (공식 통계와 r=0.999988)',
                fontsize=15.5, fontweight='bold', color=TXT, ha='center', alpha=a2, zorder=6)


# ═══ PART 3 · 지정 감사 ═════════════════════════════════════
@clip('3-1', '판정식_재현_99_4', 10)
def c31(ax, t, sec, st):
    title_bar(ax, '공표 판정식을 그대로 재계산해 검산했다')
    cx, cy, r = 60, 50, 27
    prog = ease(seg(t, 0.08, 0.62)) * 158 / 159
    ax.add_patch(Wedge((cx, cy), r, 0, 360, width=7.5, facecolor=TRACK, edgecolor='none', zorder=3))
    if prog > 0:
        ax.add_patch(Wedge((cx, cy), r, 90 - prog * 360, 90, width=7.5, facecolor=ACC,
                           edgecolor='none', zorder=4))
    n = int(prog * 159 + 0.5)
    ax.text(cx, cy + 4, f'{n} / 159', fontsize=34, fontweight='bold', color=TXT, ha='center', zorder=5)
    ax.text(cx, cy - 6, f'{prog * 100:.1f}% 재현', fontsize=18, color=AMB, ha='center', zorder=5)
    ax.text(cx, cy - 13, '분만 분야는 29/29 완전 재현', fontsize=12.5, color=MUT, ha='center', zorder=5)
    a2 = ease(seg(t, 0.62, 0.8))
    if a2 > 0:
        card_box(ax, 104, 30, 76, 44, alpha=a2)
        ax.text(142, 66, '불일치 4건 = 행정 시차의 증거', fontsize=19, fontweight='bold',
                color=AMB, ha='center', alpha=a2, zorder=5)
        rows = [('안성', '기준 미충족인데 지정 유지', '해제 시차'),
                ('완도·정선·이천', '충족인데 미지정', '반영 시차')]
        for i, (who, what, why) in enumerate(rows):
            y = 56 - i * 9
            ax.text(110, y, who, fontsize=14.5, fontweight='bold', color=TXT, alpha=a2, zorder=5)
            ax.text(110, y - 4, f'{what} — {why}', fontsize=12.5, color=MUT, alpha=a2, zorder=5)
        ax.text(142, 34.5, '지정·해제는 상시 갱신되지 않는다', fontsize=14, color=DANGER,
                ha='center', alpha=a2, fontweight='bold', zorder=5)


@clip('3-2', '공급변수_판별력_0', 9)
def c32(ax, t, sec, st):
    title_bar(ax, '공급 변수를 넣어도 판별력은 늘지 않는다', '로지스틱 회귀 · 5-겹 교차검증')
    bars = [('이동시간 2변수', BLU, 0.1), ('+ 전문의 수', '#9DB3D4', 0.38), ('+ 관내이용률', '#9DB3D4', 0.55)]
    for i, (name, color, t0) in enumerate(bars):
        a = ease(seg(t, t0, t0 + 0.18))
        if a <= 0:
            continue
        x = 30 + i * 46
        bh = 42 * a
        ax.add_patch(FancyBboxPatch((x, 30), 30, bh, boxstyle='round,pad=0.4,rounding_size=1.2',
                                    facecolor=color, edgecolor='none', alpha=0.95, zorder=4))
        if a > 0.9:
            ax.text(x + 15, 30 + bh + 3.5, 'AUC 1.000', fontsize=15, fontweight='bold',
                    color=TXT, ha='center', zorder=5)
        ax.text(x + 15, 24.5, name, fontsize=14, color=MUT, ha='center', alpha=a, zorder=5)
    a2 = ease(seg(t, 0.75, 0.92))
    if a2 > 0:
        ax.text(96, 88, '개선 폭 0 — 공급 정보를 쥐여 줘도 판정을 더 잘 맞히지 못한다',
                fontsize=18, fontweight='bold', color=ACC_T, ha='center', alpha=a2, zorder=5)
        ax.text(96, 82.5, '지정은 정말로 이동시간만 본다 · 공급 최하위 15곳의 지정 = 0곳',
                fontsize=14, color=MUT, ha='center', alpha=a2, zorder=5)


@clip('3-3', '완전사각_5곳', 9)
def c33(ax, t, sec, st):
    title_bar(ax, '거리 기준은 통과, 관내 공급은 소멸 — 완전 사각 5곳')
    spots = [('의왕시', '전문의 0.6명/10만', 0.10), ('과천시', '분만실 없음', 0.24),
             ('경기 광주시', '인구 39만', 0.38), ('울산 울주군', '분만실 없음', 0.52),
             ('울산 북구', '분만실 없음', 0.66)]
    for i, (name, desc, t0) in enumerate(spots):
        a = ease(seg(t, t0, t0 + 0.14))
        if a <= 0:
            continue
        x = 16 + i * 33
        y = 46 + (1 - a) * 5
        ping = 0.5 + 0.5 * math.sin(sec * 4 + i)
        ax.add_patch(Circle((x + 13, y + 22), 1.7 + ping * 0.8, facecolor='none', edgecolor=DANGER,
                            lw=2, alpha=(0.8 - ping * 0.4) * a, zorder=6))
        ax.add_patch(Circle((x + 13, y + 22), 1.1, facecolor=DANGER, edgecolor='none', alpha=a, zorder=6))
        card_box(ax, x, y - 6, 27, 22, alpha=a)
        ax.text(x + 13.5, y + 9, name, fontsize=15.5, fontweight='bold', color=TXT, ha='center',
                alpha=a, zorder=5)
        ax.text(x + 13.5, y + 3.5, desc, fontsize=11.5, color=MUT, ha='center', alpha=a, zorder=5)
    a2 = ease(seg(t, 0.8, 0.95))
    if a2 > 0:
        ax.text(96, 24, 'A/B/C 어떤 등급에도 없다 — 판정식의 구조가 만든 사각지대',
                fontsize=18, fontweight='bold', color=TXT, ha='center', alpha=a2, zorder=5)


@clip('3-4', '소아_유출_100', 10)
def c34(ax, t, sec, st):
    title_bar(ax, '소아청소년과 — 5개 지역 입원 전량이 관외로', '예산·함안·장성·증평·담양')
    rng = np.random.default_rng(5)
    if 'p' not in st:
        st['p'] = rng.uniform([36, 34], [72, 66], (60, 2))
        st['a'] = rng.uniform(-0.6, 0.6, 60)
        st['ph'] = rng.uniform(0, 1, 60)
    ax.add_patch(Circle((54, 50), 26, facecolor='#F0F4FA', edgecolor='#C9D4E4', lw=1.5, zorder=3))
    ax.text(54, 80, '거주 지역', fontsize=15, color=MUT, ha='center', zorder=5)
    prog = seg(t, 0.08, 0.8)
    for (p, angle, ph) in zip(st['p'], st['a'], st['ph']):
        u = min((prog * 1.3 + ph) % 1.3, 1.0)
        d = eout(u) * 92
        cx = p[0] + d * math.cos(angle * 0.5)
        cy = p[1] + d * math.sin(angle)
        if cx < 186:
            ax.add_patch(Circle((cx, cy), 0.85, facecolor=ACC, edgecolor='none',
                                alpha=0.95 - 0.3 * u, zorder=6))
    n = int(ease(seg(t, 0.25, 0.85)) * 5689)
    ax.text(140, 62, f'{n:,}건', fontsize=44, fontweight='bold', color=DANGER, ha='center', zorder=7)
    ax.text(140, 52, '관외 유출 100%', fontsize=21, fontweight='bold', color=TXT, ha='center', zorder=7)
    a2 = ease(seg(t, 0.82, 0.95))
    if a2 > 0:
        ax.text(96, 20, '중증 이송으로는 설명되지 않는다 — 동급 병원 유출 분리로 통제 (증평 96.9%)',
                fontsize=15, color=MUT, ha='center', alpha=a2, zorder=7)


# ═══ PART 4 · 배분 진단 ═════════════════════════════════════
@clip('4-1', '등급별_지원율_격차', 9)
def c41(ax, t, sec, st):
    title_bar(ax, '같은 취약지인데 등급이 다르면 지원 확률이 다르다', 'Fisher 정확검정 p=0.021')
    data = [('A등급', 53.1, '17/32곳', ACC, 0.08), ('B등급', 19.0, '4/21곳', BLU, 0.28)]
    for i, (g, v, cnt, color, t0) in enumerate(data):
        a = ease(seg(t, t0, t0 + 0.35))
        x = 40 + i * 64
        bh = v * 0.78 * a
        ax.add_patch(FancyBboxPatch((x, 26), 36, max(bh, 0.1), boxstyle='round,pad=0.4,rounding_size=1.4',
                                    facecolor=color, edgecolor='none', alpha=0.95, zorder=4))
        ax.text(x + 18, 26 + bh + 4, f'{v * a:.0f}%', fontsize=30, fontweight='bold', color=TXT,
                ha='center', zorder=5)
        ax.text(x + 18, 20, f'{g} ({cnt})', fontsize=16, color=MUT, ha='center', zorder=5)
    a2 = ease(seg(t, 0.68, 0.86))
    if a2 > 0:
        card_box(ax, 138, 44, 42, 22, alpha=a2, warn=True)
        ax.text(159, 57.5, f'오즈 {4.82 * a2:.2f}배', fontsize=26, fontweight='bold',
                color=ACC_T, ha='center', zorder=6)
        ax.text(159, 49.5, '우연으로 보기 어렵다', fontsize=13, color=TXT, ha='center', alpha=a2, zorder=6)


@clip('4-2', '설명되지_않는_배분', 9)
def c42(ax, t, sec, st):
    title_bar(ax, '그 선정은 공개 지표로 얼마나 설명되는가', '로지스틱 4변수 모형 · McFadden R²')
    x0, y0, w, h = 21, 44, 150, 18
    card_box(ax, x0, y0, w, h)
    fill = ease(seg(t, 0.1, 0.5)) * 0.163
    ax.add_patch(FancyBboxPatch((x0, y0), w * fill, h, boxstyle='round,pad=0.4,rounding_size=1.2',
                                facecolor=TEA, edgecolor='none', alpha=0.92, zorder=4))
    ax.text(x0 + w * 0.163 / 2, y0 + h / 2, f'{fill * 100:.0f}%', fontsize=19, fontweight='bold',
            color='white', ha='center', va='center', zorder=6)
    a1 = seg(t, 0.5, 0.62)
    if a1 > 0:
        qn_ = int(1 + a1 * 6)
        for i in range(qn_):
            qx = x0 + w * 0.25 + i * w * 0.115
            ax.text(qx, y0 + h / 2, '?', fontsize=24, fontweight='bold', color='#B9C4D4',
                    ha='center', va='center', zorder=6)
    ax.text(x0 + w * 0.08, y0 + h + 5, '설명됨 (접근성 축)', fontsize=14, color=TEA, ha='center', zorder=5)
    ax.text(x0 + w * 0.6, y0 + h + 5, '설명되지 않음 — 배분 규칙은 데이터 밖에 있다', fontsize=14,
            color=MUT, ha='center', zorder=5)
    a2 = ease(seg(t, 0.72, 0.9))
    if a2 > 0:
        ax.text(96, 27, '신청 여부 · 계획서 품질 · 정성 심사 80점…', fontsize=17, color=TXT,
                ha='center', alpha=a2, zorder=5)
        ax.text(96, 20.5, '그래서 필요한 것은 "명시적 규칙"이다', fontsize=19, fontweight='bold',
                color=ACC_T, ha='center', alpha=a2, zorder=5)


# ═══ PART 5 · 처방 ══════════════════════════════════════════
def _load_priority():
    df = pd.read_csv(os.path.join(BASE, '03_분석', '조원분석_검증', '최종_우선순위표_재실행.csv'),
                     encoding='utf-8-sig')
    df['시군'] = df['지역'].str.split().str[1]
    return df


@clip('5-1', '심도부담_산점도', 11)
def c51(ax, t, sec, st):
    if 'df' not in st:
        st['df'] = _load_priority()
        rng = np.random.default_rng(3)
        st['ord'] = rng.permutation(len(st['df']))
    df = st['df']
    title_bar(ax, '취약의 "깊이"와 "인원 규모"는 다른 지도를 그린다', 'A·B 53곳 · Spearman ρ = −0.190')
    x0, y0, w, h = 36, 18, 120, 64
    card_box(ax, x0, y0, w, h)
    ax.text(x0 + w / 2, y0 - 4.5, '심도 순위 S → (1위가 왼쪽)', fontsize=12.5, color=MUT, ha='center', zorder=5)
    ax.text(x0 - 4.5, y0 + h / 2, '부담 순위 B →', fontsize=12.5, color=MUT, va='center',
            rotation=90, ha='center', zorder=5)
    n_show = int(ease(seg(t, 0.05, 0.62)) * len(df))
    for k in range(n_show):
        r = df.iloc[st['ord'][k]]
        px = x0 + 4 + (r['순위S'] - 1) / 52 * (w - 8)
        py = y0 + h - 4 - (r['순위B'] - 1) / 52 * (h - 8)
        supported = '기' in r['현행']
        pop = min(1, (n_show - k) / 6)
        ax.add_patch(Circle((px, py), 1.15 + (1 - pop) * 1.2, facecolor=BLU if supported else ACC,
                            edgecolor='white', lw=0.5, alpha=0.92 * pop + 0.08, zorder=6))
    if t > 0.66:
        a = ease(seg(t, 0.66, 0.78))
        for nm, xs, yb in [('울릉 S1', 1, 53), ('양평 B1', 17, 1), ('진천 S53·B2', 53, 2)]:
            px = x0 + 4 + (xs - 1) / 52 * (w - 8)
            py = y0 + h - 4 - (yb - 1) / 52 * (h - 8)
            ax.add_patch(Circle((px, py), 2.1, facecolor='none', edgecolor=AMB, lw=2, alpha=a, zorder=7))
            ax.text(px + 2.8, py, nm, fontsize=12.5, fontweight='bold', color=AMB, va='center',
                    alpha=a, zorder=7)
    a2 = ease(seg(t, 0.82, 0.95))
    if a2 > 0:
        ax.text(96, 8.5, '상관 −0.190 — 어느 축을 보느냐가 순위를 실제로 바꾼다 · 그래서 합성하지 않고 병렬 제시한다',
                fontsize=15.5, fontweight='bold', color=TXT, ha='center', alpha=a2, zorder=7)


@clip('5-2', '유형배정_분기', 11)
def c52(ax, t, sec, st):
    title_bar(ax, '규칙 4줄로 유형을 배정한다 — 전부 정부 문서의 숫자')
    rules = [('관내 수행 ≥50건', '분만 운영지원', '1곳', TEA, 0.06),
             ('인구·수요 충족 ∧ 수행<50', '분만 설치 검토', '7곳', ACC_T, 0.24),
             ('인구 미달 ∧ 병원급 ≥1', '외래 산부인과', '13곳', AMB, 0.42),
             ('그 외', '순회진료', '32곳', BLU, 0.60)]
    for i, (cond, out, n, color, t0) in enumerate(rules):
        a = ease(seg(t, t0, t0 + 0.16))
        if a <= 0:
            continue
        y = 74 - i * 15
        card_box(ax, 16, y - 5, 66, 11, alpha=a)
        ax.text(49, y + 0.5, cond, fontsize=13.5, color=TXT, ha='center', alpha=a, zorder=5)
        ax.annotate('', xy=(100 * a + 84 * (1 - a), y + 0.5), xytext=(84, y + 0.5),
                    arrowprops=dict(arrowstyle='-|>', color=color, lw=2.5, alpha=a), zorder=5)
        card_box(ax, 102, y - 5, 52, 11, alpha=a)
        ax.add_patch(Rectangle((102, y - 5), 1.4, 11, facecolor=color, edgecolor='none', alpha=a, zorder=6))
        ax.text(112, y + 0.5, out, fontsize=15, fontweight='bold', color=TXT, alpha=a, zorder=6)
        ax.text(148, y + 0.5, n, fontsize=16, fontweight='bold', color=color, ha='center',
                alpha=a, zorder=6)
    a2 = ease(seg(t, 0.8, 0.94))
    if a2 > 0:
        ax.text(96, 11, '머신러닝이 아니라 규칙 — 과적합·라벨 누수 논쟁에서 자유롭고, 모든 판정이 소급 가능하다',
                fontsize=15, fontweight='bold', color=MUT, ha='center', alpha=a2, zorder=6)


@clip('5-3', '설치검토_7곳중_6곳_공백', 8)
def c53(ax, t, sec, st):
    title_bar(ax, '설치가 필요한 곳일수록 비어 있다')
    a1 = ease(seg(t, 0.08, 0.4))
    for i in range(7):
        x = 30 + i * 19
        filled = i == 0
        a = a1 * ease(seg(t, 0.08 + i * 0.05, 0.2 + i * 0.05))
        if a <= 0:
            continue
        color = TEA if filled else DANGER
        ax.add_patch(Circle((x, 56), 5.5, facecolor=color if filled else '#FFF3EE',
                            edgecolor=color, lw=2.5, alpha=a, zorder=5))
        ax.text(x, 56, '지원' if filled else '공백', fontsize=12.5, fontweight='bold',
                color='white' if filled else DANGER, ha='center', va='center', alpha=a, zorder=6)
    a2 = ease(seg(t, 0.55, 0.75))
    if a2 > 0:
        ax.text(96, 38, '분만 설치 검토 7곳 중 6곳 미지원', fontsize=25, fontweight='bold',
                color=TXT, ha='center', alpha=a2, zorder=6)
        ax.text(96, 30.5, '반면 완화책인 순회진료 권고 32곳 중 16곳은 이미 지원 중', fontsize=15.5,
                color=MUT, ha='center', alpha=a2, zorder=6)


@clip('5-4', '불일치_지도', 13)
def c54(ax, t, sec, st):
    if 'geo' not in st:
        gj = json.load(open(os.path.join(BASE, '02_데이터', 'skorea-municipalities-2018-geo.json'),
                            encoding='utf-8'))
        df = _load_priority()
        prov = {'32': '강원', '38': '경남'}
        feats = {}
        for f in gj['features']:
            nm, code = f['properties']['name'], str(f['properties']['code'])
            feats.setdefault(nm, []).append((prov.get(code[:2], ''), f['geometry']))
        df['권역별'] = df['지역'].str.split().str[0]

        def pick(row):
            c = feats.get(row['시군'], [])
            if len(c) == 1:
                return c[0][1]
            want = '강원' if row['권역별'] == '강원' else '경남'
            for pv, g in c:
                if pv == want:
                    return g
            return None
        df['geom'] = df.apply(pick, axis=1)
        st['geo'], st['df'] = gj, df

    def rings(geom):
        return [geom['coordinates'][0]] if geom['type'] == 'Polygon' else [p[0] for p in geom['coordinates']]

    gj, df = st['geo'], st['df']
    title_bar(ax, '깊은 곳은 비어 있고, 얕은 곳이 채워져 있다', '심도 순위는 정부 지침 임계값만으로 산출')

    def tr(lon, lat):
        return 62 + (lon - 125.7) / 4.3 * 90, 4 + (lat - 33.8) / 4.9 * 92
    base_a = ease(seg(t, 0.03, 0.2))
    patches = []
    for f in gj['features']:
        for r in rings(f['geometry']):
            patches.append(MplPolygon([tr(x, y) for x, y in r], closed=True))
    ax.add_collection(PatchCollection(patches, facecolor=(0.58, 0.65, 0.74, 0.16 * base_a),
                                      edgecolor=(1, 1, 1, 0.9 * base_a), linewidths=0.4, zorder=3))
    a_ab = ease(seg(t, 0.2, 0.42))
    reds, blues, others = [], [], []
    for _, row in df.iterrows():
        if row['geom'] is None:
            continue
        polys = [MplPolygon([tr(x, y) for x, y in r], closed=True) for r in rings(row['geom'])]
        if row['불일치'] == '상위-미지원':
            reds.append((row, polys))
        elif '기' in row['현행']:
            blues.append((row, polys))
        else:
            others.append((row, polys))
    for _, polys in others:
        ax.add_collection(PatchCollection(polys, facecolor=(0.96, 0.76, 0.68, 0.75 * a_ab),
                                          edgecolor='none', zorder=4))
    for _, polys in blues:
        ax.add_collection(PatchCollection(polys, facecolor=(0.30, 0.47, 0.76, 0.8 * a_ab),
                                          edgecolor='none', zorder=4))
    a_red = ease(seg(t, 0.45, 0.6))
    pulse = 0.5 + 0.5 * math.sin(sec * 4)
    for i, (row, polys) in enumerate(sorted(reds, key=lambda r: r[0]['순위S'])):
        aa = a_red * ease(seg(t, 0.45 + i * 0.04, 0.55 + i * 0.04))
        if aa <= 0:
            continue
        ax.add_collection(PatchCollection(polys, facecolor=(0.91, 0.30, 0.22, min(1, 0.8 + pulse * 0.2) * aa),
                                          edgecolor='white', linewidths=0.6, zorder=5))
        arr = np.array(max(rings(row['geom']), key=len))
        cx, cy = tr(arr[:, 0].mean(), arr[:, 1].mean())
        offs = {'청송군': (4.5, -3.5, 'left'), '영덕군': (4.5, 4.5, 'left'),
                '평창군': (5.5, 3.5, 'left'), '신안군': (-4, 2.5, 'right')}
        dx, dy, ha = offs.get(row['시군'], (4, 2.5, 'left'))
        ax.text(cx + dx, cy + dy, f"{row['시군']} S{row['순위S']}위", fontsize=12.5,
                fontweight='bold', color='#B23421', alpha=aa, zorder=7, ha=ha)
    a2 = ease(seg(t, 0.72, 0.88))
    if a2 > 0:
        card_box(ax, 8, 24, 44, 34, alpha=a2)
        ax.text(30, 51.5, '심도 상위 6곳 전부 공백', fontsize=16.5, fontweight='bold', color=ACC_T,
                ha='center', alpha=a2, zorder=6)
        ax.text(30, 44, '청송 1위 · 영덕 5위 · 평창 9위', fontsize=13, color=TXT, ha='center', alpha=a2, zorder=6)
        ax.text(30, 39.5, '의령 12위 · 장수 13위 · 신안 15위', fontsize=13, color=TXT, ha='center', alpha=a2, zorder=6)
        ax.text(30, 31, '반대로 심도 41·44·50위는 지원 중', fontsize=12.5, color=BLU, ha='center',
                alpha=a2, zorder=6)


# ═══ PART 6 · 제언·아웃트로 ═════════════════════════════════
@clip('6-1', '제언_5건', 10)
def c61(ax, t, sec, st):
    title_bar(ax, '다섯 개의 제언 — 각각 본문 분석 하나에 대응한다')
    items = [('①', '지정: 공급 공백형 트랙 신설', '사각지대 5곳'),
             ('②', 'TRI 관내/관외 병기', '정의의 맹점 해소'),
             ('③', '우선순위에 부담 축 병기', '계산 한 줄 추가'),
             ('④', 'B등급 공백형 별도 관리', '17곳 중 16곳 수행 0건'),
             ('⑤', '시·도 표준 우선순위표 제공', '산출물 CSV 2종이 실물')]
    for i, (no, head, tail) in enumerate(items):
        a = ease(seg(t, 0.06 + i * 0.13, 0.2 + i * 0.13))
        if a <= 0:
            continue
        y = 76 - i * 13.5
        x_off = (1 - a) * 8
        card_box(ax, 20 + x_off, y - 5, 152, 10.5, alpha=a)
        ax.add_patch(Circle((28 + x_off, y + 0.3), 3.2, facecolor=ACC, edgecolor='none', alpha=a, zorder=5))
        ax.text(28 + x_off, y + 0.3, no, fontsize=15, fontweight='bold', color='white',
                ha='center', va='center', alpha=a, zorder=6)
        ax.text(36 + x_off, y + 0.3, head, fontsize=16.5, fontweight='bold', color=TXT,
                va='center', alpha=a, zorder=5)
        ax.text(168 + x_off, y + 0.3, tail, fontsize=13, color=MUT, va='center', ha='right',
                alpha=a, zorder=5)
    a2 = ease(seg(t, 0.8, 0.94))
    if a2 > 0:
        ax.text(96, 6.5, '세 배분 제언(③④⑤)은 예산 증액 없이 가능하다 — 모든 임계값은 정부 자신의 문서에서 나온다',
                fontsize=14.5, fontweight='bold', color=TEA, ha='center', alpha=a2, zorder=5)


@clip('6-2', '타이틀_아웃트로', 9)
def c62(ax, t, sec, st):
    a1 = ease(seg(t, 0.05, 0.3))
    ax.text(96, 66, '측정과 배분 사이', fontsize=52, fontweight='bold', color=TXT, ha='center',
            alpha=a1, zorder=5)
    a15 = ease(seg(t, 0.25, 0.45))
    ax.add_patch(Rectangle((96 - 30 * a15, 57), 60 * a15, 0.9, facecolor=ACC, edgecolor='none',
                           alpha=a15, zorder=5))
    a2 = ease(seg(t, 0.4, 0.6))
    if a2 > 0:
        ax.text(96, 48, '현행 배분은 취약의 깊이를 반영한다.', fontsize=20, color=TXT, ha='center',
                alpha=a2, zorder=5)
    a3 = ease(seg(t, 0.55, 0.75))
    if a3 > 0:
        ax.text(96, 40.5, '다만 그 취약을 겪는 인원의 규모는 반영하지 않는다.', fontsize=20, color=TXT,
                ha='center', alpha=a3, zorder=5)
    a4 = ease(seg(t, 0.7, 0.88))
    if a4 > 0:
        ax.text(96, 31, '우리는 정부 자신의 기준으로 그 축을 하나 추가했다.', fontsize=21,
                fontweight='bold', color=ACC_T, ha='center', alpha=a4, zorder=5)


if __name__ == '__main__':
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(CLIPS.keys())
    print(f'{len(targets)}개 클립 렌더링:')
    for cid in targets:
        render(cid)
    print('완료')
