# -*- coding: utf-8 -*-
"""A안 핵심 가설 검증: '도시형 의료 사각지대'는 실재하는가?"""
import pandas as pd, numpy as np, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
pd.set_option('display.width', 220)

BASE = r"G:\Downloads\국립중앙의료원_헬스맵(HealthMap) 공공보건의료 통계 데이터셋_20231231"
def rd(n):
    for e in ('cp949','utf-8-sig','utf-8'):
        try: return pd.read_csv(f"{BASE}\\{n}", encoding=e, low_memory=False)
        except Exception: pass
    raise RuntimeError(n)

v = rd("의료취약지.csv"); m = rd("지역별 모니터링 지표.csv")
sgg = m[m['지역코드_구분']=='시군구'].copy()
sgg['지역코드'] = sgg['지역코드'].astype(str).str.lstrip('C')   # C11110 -> 11110
v['시군구코드'] = v['시군구코드'].astype(str)
df = v.merge(sgg, left_on='시군구코드', right_on='지역코드', how='inner', suffixes=('','_m'))
print("병합 결과:", df.shape, "| 시군구", df['시군구코드'].nunique())

ACC  = '접근성취약인구율_소아청소년과(60분)(백분율)'
SPEC = '소아청소년과 전문의(전체 의료기관)(인구10만 명당 개수)'
IN   = '관내의료이용률_소아청소년과(백분율)'
TRI  = '기준시간내의료이용률_소아청소년과(60분)(백분율)'

df['취약지_소아'] = (df['소아청소년과_취약지']=='Y').astype(int)

print("\n" + "="*78)
print("[가설] 접근성(거리)은 좋은데 공급(전문의)은 부족한 지역이 존재하는가?")
print("="*78)
# 거리 기준으로는 문제없음(접근성취약인구율 0) = 현행 제도 관심 밖
near = df[df[ACC] <= 1].copy()
print(f"접근성취약인구율 <= 1%인 시군구: {len(near)}개  (현행 제도상 '거리 문제 없음')")
q = near[SPEC].quantile([.10,.25,.50,.75,.90])
print("\n그 안에서 소아청소년과 전문의 수(인구10만명당) 분포:")
print(q.round(2).to_string())
print(f"  → 최소 {near[SPEC].min():.1f}  vs  최대 {near[SPEC].max():.1f}   ({near[SPEC].max()/max(near[SPEC].min(),0.01):.0f}배 격차)")

print("\n▼ '거리는 가깝지만 전문의는 최하위' = 도시형 사각지대 후보 TOP 12")
cand = near.nsmallest(12, SPEC)[['시도명','시군구명',SPEC,ACC,IN,'인구수(명)','노인인구비율(백분율)','취약지_소아']]
cand.columns = ['시도','시군구','전문의/10만','접근성취약%','관내이용률%','인구','노인%','공식지정']
print(cand.to_string(index=False))

print("\n[대조] 공식 지정된 소아청소년과 취약지 18곳")
off = df[df['취약지_소아']==1][['시도명','시군구명',SPEC,ACC,IN,'인구수(명)']]
off.columns = ['시도','시군구','전문의/10만','접근성취약%','관내이용률%','인구']
print(off.to_string(index=False))

print("\n" + "="*78)
print("[검증] 후보군이 실제로 문제가 있는가? — 관내의료이용률로 확인")
print("="*78)
cand_codes = set(near.nsmallest(20, SPEC)['시군구코드'])
df['그룹'] = np.where(df['취약지_소아']==1,'①공식지정(18)',
             np.where(df['시군구코드'].isin(cand_codes),'②사각지대후보(20)','③기타(212)'))
print(df.groupby('그룹')[[IN, TRI, SPEC]].median().round(2).to_string())
print("\n※ 관내의료이용률이 낮다 = 지역 밖으로 원정 진료를 나간다 = 실질 공급 부족 신호")
