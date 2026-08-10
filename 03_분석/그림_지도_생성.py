# -*- coding: utf-8 -*-
"""
그림 4종 + 시도별 우선순위표 생성 (결과보고서·PPT·시연영상용)

입력:
  03_분석/조원분석_검증/최종_우선순위표_재실행.csv  (A·B 53곳, 노트북 재실행 산출)
  02_데이터/skorea-municipalities-2018-geo.json     (통계청 시군구 경계, southkorea-maps)
출력:
  04_제출물/그림/그림1_심도부담_산점도.png
  04_제출물/그림/그림2_등급별_지원율.png
  04_제출물/그림/그림3_배정_교차표.png
  04_제출물/그림/그림4_지도_우선순위.png
  04_제출물/시도별_우선순위표.csv
"""
import json, os, sys, io
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon, Patch
from matplotlib.collections import PatchCollection
from matplotlib.lines import Line2D
from scipy import stats

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(BASE, '03_분석', '조원분석_검증', '최종_우선순위표_재실행.csv')
GEO = os.path.join(BASE, '02_데이터', 'skorea-municipalities-2018-geo.json')
OUT = os.path.join(BASE, '04_제출물', '그림')
os.makedirs(OUT, exist_ok=True)

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
NAVY, BLUE, RED, GRAY = '#17456b', '#3E6DB5', '#E85D42', '#c8d0d8'

df = pd.read_csv(CSV, encoding='utf-8-sig')
df['권역'] = df['지역'].str.split().str[0]
df['시군'] = df['지역'].str.split().str[1]
assert len(df) == 53, len(df)

# ── 검증: 본문 수치와 일치 확인 ─────────────────────────────
rho, rho_p = stats.spearmanr(df['순위S'], df['순위B'])
ct = pd.crosstab(df['등급'], df['현행'])
sup_col = [c for c in ct.columns if '기' in c][0]
uns_col = [c for c in ct.columns if '미' in c][0]
a_sup, a_uns = ct.loc['A', sup_col], ct.loc['A', uns_col]
b_sup, b_uns = ct.loc['B', sup_col], ct.loc['B', uns_col]
odds, fisher_p = stats.fisher_exact([[a_sup, a_uns], [b_sup, b_uns]])
print(f"심도-부담 순위상관 rho={rho:.3f} (기대 -0.190)")
print(f"A {a_sup}/{a_sup+a_uns} vs B {b_sup}/{b_sup+b_uns}, OR={odds:.2f}, p={fisher_p:.3f} (기대 4.82, 0.021)")

# ── 그림 1: 심도-부담 산점도 ────────────────────────────────
fig, ax = plt.subplots(figsize=(7.6, 6.4), dpi=200)
for label, sub, c, m in [('기 지원 (21곳)', df[df['현행'].str.contains('기')], BLUE, 'o'),
                          ('미지원 (32곳)', df[df['현행'].str.contains('미')], RED, 's')]:
    ax.scatter(sub['순위S'], sub['순위B'], s=46, c=c, marker=m, alpha=.75,
               edgecolors='white', linewidths=.6, label=label, zorder=3)
med = 27
ax.axvline(med, color=GRAY, lw=1, ls='--', zorder=1)
ax.axhline(med, color=GRAY, lw=1, ls='--', zorder=1)
ax.text(1.2, 4.2, '심도·부담 모두 상위\n(설치·운영 후보)', fontsize=8.5, color='#666', va='top')
for _, r in df.iterrows():
    if r['순위S'] <= 3 or r['순위B'] <= 3:
        right_edge = r['순위S'] > 45
        stack = (r['순위S'] <= 3 and r['순위B'] >= 45)   # 좌하단 밀집(울릉·영양)
        dx, dy = (-7, 5) if right_edge else ((7, -3 - 8 * (r['순위B'] % 2)) if stack else (6, 5))
        ax.annotate(r['시군'], (r['순위S'], r['순위B']), fontsize=8, color=NAVY,
                    xytext=(dx, dy), textcoords='offset points',
                    ha='right' if right_edge else 'left')
ax.invert_yaxis()   # 부담 1위(가장 많음)를 위로
ax.set_xlabel('심도 순위 S (1 = 취약이 가장 깊음)', fontsize=10)
ax.set_ylabel('부담 순위 B (1 = 미충족 분만 가장 많음)', fontsize=10)
ax.set_title('취약의 "깊이"와 "인원 규모"는 다른 지도를 그린다', fontsize=12.5, color=NAVY, pad=12)
ax.text(.5, 1.005, f'A·B 53곳 · Spearman ρ = {rho:.3f} — 어느 축을 보느냐가 순위를 실제로 바꾼다',
        transform=ax.transAxes, ha='center', fontsize=9, color='#555')
ax.legend(loc='lower right', fontsize=9, framealpha=.9)
ax.grid(alpha=.25)
fig.tight_layout()
fig.savefig(os.path.join(OUT, '그림1_심도부담_산점도.png'), bbox_inches='tight')
plt.close(fig)

# ── 그림 2: 등급별 지원율 ──────────────────────────────────
fig, ax = plt.subplots(figsize=(6.4, 5.2), dpi=200)
grades = ['A', 'B']
rates = [a_sup/(a_sup+a_uns)*100, b_sup/(b_sup+b_uns)*100]
ns = [(a_sup, a_sup+a_uns), (b_sup, b_sup+b_uns)]
bars = ax.bar(grades, rates, width=.52, color=[NAVY, '#7a93a8'])
for bar, rate, (k, n) in zip(bars, rates, ns):
    ax.text(bar.get_x()+bar.get_width()/2, rate+1.5, f'{rate:.0f}%\n({k}/{n}곳)',
            ha='center', fontsize=11, color=NAVY, fontweight='bold')
ax.set_ylim(0, 72)
ax.set_ylabel('외래·순회 수준 지원을 받은 비율 (%)', fontsize=10)
ax.set_xlabel('분만취약지 등급 (A = 접근성·이용률 이중 충족, B = 단일 충족)', fontsize=10)
ax.set_title('같은 취약지인데 등급이 다르면 지원 확률이 다르다', fontsize=12.5, color=NAVY, pad=12)
ax.text(.5, 1.005, f'A등급의 지원 오즈는 B등급의 {odds:.2f}배 (Fisher 정확검정 p = {fisher_p:.3f})',
        transform=ax.transAxes, ha='center', fontsize=9, color='#555')
ax.grid(axis='y', alpha=.25)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(os.path.join(OUT, '그림2_등급별_지원율.png'), bbox_inches='tight')
plt.close(fig)

# ── 그림 3: 유형 배정 교차표 ────────────────────────────────
type_order = [t for t in ['분만 설치 검토', '분만 운영지원', '외래 산부인과', '순회진료']
              if t in df['권고유형'].unique()]
type_order += [t for t in df['권고유형'].unique() if t not in type_order]
xt = pd.crosstab(df['권고유형'], df['현행']).reindex(type_order)[[sup_col, uns_col]]
fig, ax = plt.subplots(figsize=(7.0, 4.6), dpi=200)
data = xt.values
im_colors = np.zeros(data.shape + (4,))
for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        base = np.array(matplotlib.colors.to_rgba(NAVY if j == 0 else RED))
        alpha = 0.12 + 0.55 * data[i, j] / data.max()
        im_colors[i, j] = base * [1, 1, 1, 0] + [0, 0, 0, alpha]
        im_colors[i, j, :3] = base[:3]
ax.imshow(im_colors, aspect='auto')
for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        ax.text(j, i, f'{data[i,j]}곳', ha='center', va='center', fontsize=13,
                color='white' if data[i, j] / data.max() > .45 else NAVY, fontweight='bold')
ax.set_xticks([0, 1]); ax.set_xticklabels([f'{sup_col} (21곳)', f'{uns_col} (32곳)'], fontsize=10)
ax.set_yticks(range(len(xt))); ax.set_yticklabels([f'{t}\n({int(data[i].sum())}곳)' for i, t in enumerate(xt.index)], fontsize=9.5)
ax.set_title('모형의 유형 배정 vs 현행 지원 — 설치가 필요한 곳일수록 비어 있다', fontsize=12, color=NAVY, pad=12)
inst_row = [i for i, t in enumerate(xt.index) if '설치' in t]
if inst_row:
    i = inst_row[0]
    ax.add_patch(plt.Rectangle((.5, i-.48), .96, .96, fill=False, edgecolor=RED, lw=2.4))
    ax.text(1, i+.3, '설치 검토 7곳 중 6곳 미지원', ha='center', fontsize=9.5,
            color=RED, fontweight='bold')
ax.set_xlabel('현행 지원 여부 (외래·순회 수준)', fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(OUT, '그림3_배정_교차표.png'), bbox_inches='tight')
plt.close(fig)

# ── 지도 준비: 시군명 → 폴리곤 매칭 ─────────────────────────
gj = json.load(open(GEO, encoding='utf-8'))
PROV = {'11': '서울', '21': '부산', '22': '대구', '23': '인천', '24': '광주', '25': '대전',
        '26': '울산', '29': '세종', '31': '경기', '32': '강원', '33': '충북', '34': '충남',
        '35': '전북', '36': '전남', '37': '경북', '38': '경남', '39': '제주'}
feats = {}
for f in gj['features']:
    name, code = f['properties']['name'], str(f['properties']['code'])
    feats.setdefault(name, []).append((PROV.get(code[:2], code[:2]), f))

def match_feature(row):
    cands = feats.get(row['시군'], [])
    if len(cands) == 1:
        return cands[0]
    if row['시군'] == '고성군':          # 강원 고성군 / 경남 고성군 중복
        want = '강원' if row['권역'] == '강원' else '경남'
        for prov, f in cands:
            if prov == want:
                return (prov, f)
    return (None, None)

df['시도'] = None
polys = {}
for idx, row in df.iterrows():
    prov, f = match_feature(row)
    if f is None:
        print(f"  !! 매칭 실패: {row['지역']}")
        continue
    df.at[idx, '시도'] = prov
    polys[idx] = f['geometry']
print(f"지도 매칭: {len(polys)}/53")

def rings(geom):
    if geom['type'] == 'Polygon':
        return [geom['coordinates'][0]]
    return [p[0] for p in geom['coordinates']]

# ── 그림 4: 지도 — 우선순위 상위인데 미지원인 지역 ─────────
fig, ax = plt.subplots(figsize=(8.4, 10.2), dpi=200)
bg = []
for f in gj['features']:
    for r in rings(f['geometry']):
        bg.append(MplPolygon(r, closed=True))
ax.add_collection(PatchCollection(bg, facecolor='#f0f2f4', edgecolor='#d4dade', linewidths=.35))

top_unsup = df[df['불일치'] == '상위-미지원'].sort_values('순위S')
low_sup = df[df['불일치'] == '하위-기지원'].sort_values('순위S')
for idx, row in df.iterrows():
    if idx not in polys:
        continue
    supported = '기' in row['현행']
    is_top_unsup = row['불일치'] == '상위-미지원'
    fc = BLUE if supported else (RED if is_top_unsup else '#F2C0B0')
    pcs = [MplPolygon(r, closed=True) for r in rings(polys[idx])]
    ax.add_collection(PatchCollection(pcs, facecolor=fc, edgecolor='white', linewidths=.5,
                                      zorder=3 if is_top_unsup else 2))

def ring_area(r):
    a = np.array(r)
    x, y = a[:, 0], a[:, 1]
    return .5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

def centroid(idx):
    arr = np.array(max(rings(polys[idx]), key=ring_area))   # 면적 최대 링 (군도 대응)
    return arr[:, 0].mean(), arr[:, 1].mean()

RED_OFFSET = {'신안군': (-16, -26, 'right')}   # 군도: 좌하단 바다 쪽으로
for k, (idx, row) in enumerate(top_unsup.iterrows()):
    if idx not in polys:
        continue
    dx, dy, ha = RED_OFFSET.get(row['시군'], (16, 9 if k % 2 == 0 else -15, 'left'))
    ax.annotate(f"{row['시군']} S{row['순위S']}위 · 미지원", centroid(idx), fontsize=8.5,
                color='white', fontweight='bold', ha=ha, va='center', xytext=(dx, dy),
                textcoords='offset points', zorder=5, annotation_clip=False,
                arrowprops=dict(arrowstyle='-', color=RED, lw=.9),
                bbox=dict(boxstyle='round,pad=0.24', fc=RED, ec='white', lw=.6, alpha=.95))
for idx, row in low_sup.iterrows():
    if idx not in polys:
        continue
    blue_dx, blue_dy = (26, -22) if row['시군'] == '함평군' else (-58, -16)
    ax.annotate(f"{row['시군']} S{row['순위S']}위 · 기지원", centroid(idx), fontsize=8,
                color=NAVY, ha='left', va='center', xytext=(blue_dx, blue_dy),
                textcoords='offset points', zorder=5,
                arrowprops=dict(arrowstyle='-', color=BLUE, lw=.8),
                bbox=dict(boxstyle='round,pad=0.22', fc='white', ec=BLUE, lw=.8, alpha=.92))
ax.set_xlim(125.7, 130.0); ax.set_ylim(33.8, 38.65)
ax.set_aspect(1.23)
ax.axis('off')
ax.set_title('배분과 취약 심도의 불일치 지도 — 깊은 곳은 비어 있고, 얕은 곳이 채워져 있다',
             fontsize=12.5, color=NAVY, pad=14)
legend = [Patch(fc=RED, label=f'심도 상위인데 미지원 ({len(top_unsup)}곳)'),
          Patch(fc='#F2C0B0', label=f'그 외 미지원 A·B ({int(df["현행"].str.contains("미").sum()) - len(top_unsup)}곳)'),
          Patch(fc=BLUE, label=f'기 지원 A·B (21곳, 이 중 심도 하위 {len(low_sup)}곳 별도 표기)'),
          Patch(fc='#f0f2f4', ec='#d4dade', label='그 외 시군구')]
ax.legend(handles=legend, loc='upper left', fontsize=9, framealpha=.95)
ax.text(0, -.01, '자료: 헬스맵(2023)·복지부 공고 제2026-144호 — 심도 순위 S는 정부 지침 임계값만으로 산출',
        transform=ax.transAxes, fontsize=8, color='#777', va='top')
fig.savefig(os.path.join(OUT, '그림4_지도_우선순위.png'), bbox_inches='tight')
plt.close(fig)

# ── 시도별 우선순위표 ──────────────────────────────────────
tbl = df[['시도', '지역', '등급', '순위S', '순위B', '미충족분만', '권고유형', '현행', '불일치']].copy()
tbl = tbl.sort_values(['시도', '순위S'])
tbl['시도내순위'] = tbl.groupby('시도')['순위S'].rank(method='min').astype(int)
tbl = tbl[['시도', '시도내순위', '지역', '등급', '순위S', '순위B', '미충족분만', '권고유형', '현행', '불일치']]
out_csv = os.path.join(BASE, '04_제출물', '시도별_우선순위표.csv')
tbl.to_csv(out_csv, index=False, encoding='utf-8-sig')
print(f"시도별 표: {out_csv} ({len(tbl)}행, {tbl['시도'].nunique()}개 시도)")
print(tbl.groupby('시도').size().to_dict())
print("상위-미지원:", top_unsup['지역'].tolist())
