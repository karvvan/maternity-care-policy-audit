# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
pd.set_option('display.width', 200)

BASE = r"G:\Downloads\국립중앙의료원_헬스맵(HealthMap) 공공보건의료 통계 데이터셋_20231231"

def rd(name):
    for enc in ('cp949','utf-8-sig','utf-8'):
        try:
            return pd.read_csv(f"{BASE}\\{name}", encoding=enc, low_memory=False)
        except Exception:
            continue
    raise RuntimeError(name)

v = rd("의료취약지.csv")
m = rd("지역별 모니터링 지표.csv")

print("="*70)
print("[1] 의료취약지.csv  shape =", v.shape)
for c in ['분만_A취약지','소아청소년과_취약지','인공신장실_취약지','응급_취약지']:
    print(f"    {c:20s} 취약지 {int((v[c]=='Y').sum()):3d} / {len(v)}")

print("\n[2] 제도는 무엇을 보고 판정하는가 — 응급취약지 vs 비취약지")
v['응급라벨'] = (v['응급_취약지']=='Y').astype(int)
cols = ['인구수(명)','노인인구비율(백분율)','재정자립도(백분율)',
        '의료급여 수급자 비율(백분율)','면적당의원(100제곱킬로미터당 개수)']
g = v.groupby('응급라벨')[cols].median().T
g.columns = ['비취약지(148)','취약지(102)']
print(g.round(2).to_string())

print("\n[3] 지역별 모니터링 지표  shape =", m.shape)
sgg = m[m['지역코드_구분']=='시군구'].copy()
print("    시군구 행 =", len(sgg))

key = [c for c in m.columns if any(k in c for k in
      ['소아청소년과 전문의(전체','접근성취약인구율_지역응급의료센터','접근성취약인구율_소아청소년과',
       '기준시간내의료이용률_지역응급의료센터','관내의료이용률_응급실','관내의료이용률_소아청소년과',
       '치료가능사망률','영아사망률'])]
print("\n[4] 핵심 지표 결측 현황 (시군구 250개 기준)")
for c in key:
    nn = sgg[c].notna().sum()
    print(f"    {'OK ' if nn>200 else '!! '}{c[:60]:62s} 값존재 {nn:3d}/250")
