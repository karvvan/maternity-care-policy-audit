# -*- coding: utf-8 -*-
"""
본분석 보완 (2026-08-04)
  [F'] 요양종별 OD 코드 조인 수정 → 핵심 5곳 동급(의원·병원·종합병원) 유출 분리
  [I]  분만 사각지대 8곳 — 산부인과 입원 OD 유출률·행선지
  [J]  유형II 내부 단계화: 신규 지정을 (완전 사각/경계/기존중복)으로 분해 + 관내이용률 0% 소계
  [K]  응급 후보 성격 분석: 대도시 구의 '관내 응급기관 부재' 현상
"""
import pandas as pd, numpy as np, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
pd.set_option('display.width', 240)

BASE = r"G:\Downloads\국립중앙의료원_헬스맵(HealthMap) 공공보건의료 통계 데이터셋_20231231"
HERE = os.path.dirname(os.path.abspath(__file__))
LOG  = os.path.join(HERE, "본분석_보완로그.txt")
_buf=[]; _p=print
def print(*a,**k): _p(*a,**k); _buf.append(' '.join(str(x) for x in a))

def rd(n):
    for e in ('cp949','utf-8-sig','utf-8'):
        try: return pd.read_csv(os.path.join(BASE,n), encoding=e, low_memory=False)
        except UnicodeDecodeError: continue

v = rd("의료취약지.csv"); m = rd("지역별 모니터링 지표.csv")
sgg = m[m['지역코드_구분'].astype(str).str.contains('시군구', na=False)].copy()
sgg['code'] = sgg['지역코드'].astype(str).str.extract(r'(\d+)').astype(int)
v2 = v.copy(); v2['code'] = v2['시군구코드'].astype(int)
d = sgg.merge(v2, on='code', how='inner', suffixes=('','_y'))
num = lambda c: pd.to_numeric(d[c], errors='coerce')
d['name'] = d['시도명'].astype(str)+' '+d['시군구명'].astype(str)
code2name = dict(zip(d['code'], d['name']))
name2code = {r['name']: r['code'] for _,r in d.iterrows()}

SEC = lambda t: print("\n"+"="*100+f"\n{t}\n"+"="*100)

CORE5 = ['충청남도 예산군','경상남도 함안군','전라남도 장성군','충청북도 증평군','전라남도 담양군']
BIRTH8 = ['경기도 의왕시','충청남도 계룡시','전라남도 장성군','울산광역시 울주군',
          '경기도 광주시','울산광역시 북구','경상북도 예천군','경기도 과천시']

# [F'] 요양종별 OD — 코드 조인 --------------------------------------------
SEC("[F'] 핵심 5곳 — 요양종별 OD (전 진료과 합산) 동급 유출 분리")
od = rd("유출입_요양종별.csv")
od['c1']=pd.to_numeric(od['지역1'],errors='coerce'); od['c2']=pd.to_numeric(od['지역2'],errors='coerce')
tiers = {'동급(의원+병원+종합)':['의원','병원','종합병원'], '상급종합':['상급종합병원']}
sub_all = od[od['중분류'].isin(['의원','병원','종합병원'])]
tot_all = sub_all.groupby('c2')['입원건수'].sum()
intra_all = sub_all[sub_all['c1']==sub_all['c2']].groupby('c2')['입원건수'].sum()
out_all = (1-intra_all.reindex(tot_all.index).fillna(0)/tot_all)*100
print(f"  전국 동급 유출률 중앙값: {out_all.median():.1f}%")
for nm in CORE5:
    c = name2code[nm]; parts=[f"  {nm:14s}"]
    for lab,ts in tiers.items():
        s = od[(od['c2']==c) & (od['중분류'].isin(ts))]
        tot = s['입원건수'].sum(); intra = s[s['c1']==c]['입원건수'].sum()
        pct = 100*(1-intra/tot) if tot else float('nan')
        parts.append(f"{lab} 유출 {pct:5.1f}% ({tot:,.0f}건)")
    print(" | ".join(parts))

# [I] 분만 사각지대 — 산부인과 OD ------------------------------------------
SEC("[I] 분만 사각지대 8곳 — 산부인과 입원 유출률·주요 행선지")
odp = rd("유출입_진료과목.csv")
odp['c1']=pd.to_numeric(odp['지역1'],errors='coerce'); odp['c2']=pd.to_numeric(odp['지역2'],errors='coerce')
gyn = odp[odp['중분류']=='산부인과']
tot_g = gyn.groupby('c2')['입원건수'].sum()
intra_g = gyn[gyn['c1']==gyn['c2']].groupby('c2')['입원건수'].sum()
out_g = (1-intra_g.reindex(tot_g.index).fillna(0)/tot_g)*100
print(f"  전국 산부인과 유출률 중앙값: {out_g.median():.1f}%")
for nm in BIRTH8:
    c = name2code[nm]
    dest = gyn[(gyn['c2']==c)&(gyn['c1']!=c)].nlargest(3,'입원건수')
    ds = ' · '.join(f"{code2name.get(r['c1'],int(r['c1']))}({r['입원건수']:.0f})" for _,r in dest.iterrows())
    t = tot_g.get(c,0)
    print(f"  {nm:14s} 유출률 {out_g.get(c,float('nan')):5.1f}% (총 {t:,.0f}건)  → {ds}")

# 소아 핵심 5곳 소아과 유출도 최종 확정치로 재출력
SEC("[I-2] 소아 핵심 5곳 — 소아청소년과 입원 유출률·행선지 (확정)")
ped = odp[odp['중분류']=='소아청소년과']
tot_p = ped.groupby('c2')['입원건수'].sum()
intra_p = ped[ped['c1']==ped['c2']].groupby('c2')['입원건수'].sum()
out_p = (1-intra_p.reindex(tot_p.index).fillna(0)/tot_p)*100
print(f"  전국 소아과 유출률 중앙값: {out_p.median():.1f}%")
tot5 = 0
for nm in CORE5:
    c = name2code[nm]
    dest = ped[(ped['c2']==c)&(ped['c1']!=c)].nlargest(3,'입원건수')
    ds = ' · '.join(f"{code2name.get(r['c1'],int(r['c1']))}({r['입원건수']:.0f})" for _,r in dest.iterrows())
    t = tot_p.get(c,0); tot5 += t
    print(f"  {nm:14s} 유출률 {out_p.get(c,float('nan')):5.1f}% (총 {t:,.0f}건)  → {ds}")
print(f"  ▶ 5곳 합계 소아 입원 {tot5:,.0f}건")

# [J] 유형II 단계화 ---------------------------------------------------------
SEC("[J] 유형II [공급≤지정지중앙값 ∧ 관내이용률≤15] 신규 지정의 내부 구성")
FLD = {
 '소아': dict(Y=d['소아청소년과_취약지'].eq('Y'), acc=num('소아청소년과_접근성취약인구비율(백분율)'),
              loc=num('관내의료이용률_소아청소년과(백분율)'),
              sup=num('소아청소년과 전문의(전체 의료기관)(인구10만 명당 개수)')),
 '분만': dict(Y=d['분만_A취약지'].eq('Y'), acc=num('분만_접근성취약인구비율(백분율)'),
              loc=num('관내의료이용률_분만실(백분율)'),
              sup=num('산부인과 전문의(전체 의료기관)(인구10만 명당 개수)')),
}
for f,x in FLD.items():
    off = x['sup'][x['Y']].median()
    t2 = d[(x['sup']<=off) & (x['loc']<=15) & (~x['Y'])].copy()
    t2['acc_v']=x['acc']; t2['loc_v']=x['loc']
    full_blind = t2[t2['acc_v']<=1]          # 거리 완전 통과 = 현행 제도 시야 밖
    border     = t2[(t2['acc_v']>1)]         # 거리 경계(1~30) = 차상위 성격
    zero       = t2[t2['loc_v']==0]
    print(f"\n  {f}: 유형II 신규 {len(t2)}곳 = 완전 사각(접근성≤1%) {len(full_blind)}곳 + 거리 경계(1%~) {len(border)}곳")
    print(f"      관내이용률 0%(관내 공급 사실상 부재): {len(zero)}곳")
    print(f"      완전 사각 명단: {sorted(full_blind['name'].tolist())}")

# [K] 응급 후보 성격 --------------------------------------------------------
SEC("[K] 응급 — '관내 응급의료기관 부재' 시군구 전수 (대도시 구 포함)")
d['em_sup'] = num('응급의료기관(100제곱킬로미터당 개수)')
d['em_loc'] = num('관내의료이용률_응급실(백분율)')
noem = d[(d['em_sup']==0)]
urban = noem[noem['name'].str.contains('특별시|광역시|수원시|용인시|성남시|고양시|안양시|하남시')]
print(f"  응급의료기관 밀도 0인 시군구: {len(noem)}곳 / 그중 대도시 자치구·수도권 시: {len(urban)}곳")
print(f"  대도시권 예시: {sorted(urban['name'].tolist())[:12]}")
print(f"  이들의 응급실 관내이용률 중앙값: {noem['em_loc'].median():.1f}%")

with open(LOG,'w',encoding='utf-8') as fp: fp.write('\n'.join(_buf))
_p(f"\n[로그 저장] {LOG}")
