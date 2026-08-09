# -*- coding: utf-8 -*-
"""
본분석 (2026-08-04) — 결과보고서 최종본에 들어가는 전체 실측
  [A] 지정 규칙 역공학: 4분야 결정론적 재현 + 오탐/누락 식별
  [B] EDA 확정 수치: 프로파일 / 거리통과 내부 공급격차 / 분야별 지정률
  [C] 사각지대 탐지 4분야 확장 (소아·분만·투석·응급)
  [D] 유형II 임계값 민감도 스윕 (전문의 4~7 × 관내이용률 10~25%)
  [E] 소아 오탐 2곳 원인 조사
  [F] OD 요양종별 — 동급(의원·병원) 유출 분리 재검
  [G] 로지스틱 5-fold CV — 공급 무관성 (소아·분만)
  [H] 보상형 지수 실패 재현 + 이중 트랙 최종안 + 차상위 명단
실행: python main_01_본분석.py  (결과는 stdout + ../03_분석/본분석_결과로그.txt)
"""
import pandas as pd, numpy as np, sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
pd.set_option('display.width', 240)

BASE = r"G:\Downloads\국립중앙의료원_헬스맵(HealthMap) 공공보건의료 통계 데이터셋_20231231"
HERE = os.path.dirname(os.path.abspath(__file__))
LOG  = os.path.join(HERE, "본분석_결과로그.txt")
_buf = []
_orig_print = print
def print(*a, **k):
    _orig_print(*a, **k)
    _buf.append(' '.join(str(x) for x in a))

def rd(n):
    for e in ('cp949','utf-8-sig','utf-8'):
        try: return pd.read_csv(os.path.join(BASE,n), encoding=e, low_memory=False)
        except UnicodeDecodeError: continue

v = rd("의료취약지.csv"); m = rd("지역별 모니터링 지표.csv")
sgg = m[m['지역코드_구분'].astype(str).str.contains('시군구', na=False)].copy()
sgg['code'] = sgg['지역코드'].astype(str).str.extract(r'(\d+)').astype(int)
v2 = v.copy(); v2['code'] = v2['시군구코드'].astype(int)
d = sgg.merge(v2, on='code', how='inner', suffixes=('','_v'))
num = lambda c: pd.to_numeric(d[c], errors='coerce')
d['name'] = d['시도명'].astype(str) + ' ' + d['시군구명'].astype(str)
print(f"마스터 조인: {len(d)}곳 (코드 조인, 무손실)")

# 분야 공통 지표 사전 ------------------------------------------------------
F = {
 '소아': dict(Y=d['소아청소년과_취약지'].eq('Y'),
              acc=num('소아청소년과_접근성취약인구비율(백분율)'),
              tri=num('소아청소년과_TRI(백분율)'),
              loc=num('관내의료이용률_소아청소년과(백분율)'),
              sup=num('소아청소년과 전문의(전체 의료기관)(인구10만 명당 개수)'),
              sup_name='소아청소년과 전문의/10만명'),
 '분만': dict(Y=d['분만_A취약지'].eq('Y'),
              acc=num('분만_접근성취약인구비율(백분율)'),
              tri=num('분만_TRI(백분율)'),
              loc=num('관내의료이용률_분만실(백분율)'),
              sup=num('산부인과 전문의(전체 의료기관)(인구10만 명당 개수)'),
              sup_name='산부인과 전문의/10만명'),
 '투석': dict(Y=d['인공신장실_취약지'].eq('Y'),
              acc=num('인공신장실_접근성취약인구비율(백분율)'),
              tri=num('인공신장실_TRI(백분율)'),
              loc=num('관내의료이용률_투석(백분율)'),
              sup=None,  # 공급 직접 컬럼 부재 → 2중 기준 + 한계 명시
              sup_name='(공급 컬럼 부재)'),
}
d['a30'] = num('접근성취약인구율_지역응급의료센터(30분)(백분율)')
d['a60'] = num('접근성취약인구율_권역응급의료센터(60분)(백분율)')
EM = dict(Y=d['응급_취약지'].eq('Y'),
          loc=num('관내의료이용률_응급실(백분율)'),
          sup=num('응급의료기관(100제곱킬로미터당 개수)'),
          sup_name='응급의료기관/100km²')
d['pop'] = num('인구수(명)')

SEC = lambda t: print("\n"+"="*100+f"\n{t}\n"+"="*100)

# [A] 규칙 재현 ------------------------------------------------------------
SEC("[A] 지정 규칙 역공학 — 4분야 결정론적 재현")
tot_match = tot_pos = 0
for f,x in F.items():
    pred = (x['acc']>=30) & (x['tri']<30)
    tp = int((pred & x['Y']).sum()); fp = int((pred & ~x['Y']).sum()); fn = int(((~pred) & x['Y']).sum())
    tot_match += tp; tot_pos += int(x['Y'].sum())
    print(f"  {f}: 규칙[접근성≥30 ∧ TRI<30] → 일치 {tp}/{int(x['Y'].sum())}  오탐 {fp}  누락 {fn}")
pred_em = (d['a30']>=27) | (d['a60']>=27)
tp = int((pred_em & EM['Y']).sum()); fp = int((pred_em & ~EM['Y']).sum()); fn = int(((~pred_em) & EM['Y']).sum())
tot_match += tp; tot_pos += int(EM['Y'].sum())
print(f"  응급: 규칙[30분≥27% ∨ 60분≥27%] → 일치 {tp}/{int(EM['Y'].sum())}  오탐 {fp}  누락 {fn}")
print(f"  ▶ 전체 재현율: {tot_match}/{tot_pos} = {100*tot_match/tot_pos:.1f}%")

# [B] EDA ------------------------------------------------------------------
SEC("[B] EDA 확정 수치")
em_y = EM['Y']
prof_cols = {'인구수(명)':'인구', '노인인구비율(백분율)':'노인비율',
             '재정자립도(백분율)':'재정자립도', '면적당의원(100제곱킬로미터당 개수)':'면적당 의원'}
print("  응급 취약지 vs 비취약지 (중앙값):")
for c,lab in prof_cols.items():
    a = num(c)[~em_y].median(); b = num(c)[em_y].median()
    print(f"    {lab}: 비취약 {a:,.2f} / 취약 {b:,.2f}  ({a/b if b else float('nan'):.1f}배)")
print(f"\n  분야별 지정률: 응급 {100*em_y.mean():.1f}% | 분만 {100*F['분만']['Y'].mean():.1f}% | "
      f"소아 {100*F['소아']['Y'].mean():.1f}% | 투석 {100*F['투석']['Y'].mean():.1f}%")
for f in ['소아','분만']:
    x=F[f]; passed = d[x['acc']<=1]
    s = x['sup'][x['acc']<=1]
    print(f"\n  거리통과(접근성≤1%) {len(passed)}곳 내부 {x['sup_name']} 분포: "
          f"10% {s.quantile(.1):.2f} · 중앙값 {s.median():.2f} · 90% {s.quantile(.9):.2f} · "
          f"min {s.min():.2f} ~ max {s.max():.2f} ({s.max()/max(s.min(),1e-9):.0f}배)")

# [C] 사각지대 4분야 -------------------------------------------------------
SEC("[C] 사각지대 탐지 — 4분야 확장 (기준: 거리통과 ∧ 공급≤지정지중앙값 ∧ 관내이용률≤15 ∧ 미지정)")
blind = {}
for f in ['소아','분만']:
    x=F[f]
    off_med = x['sup'][x['Y']].median()
    c = d[(x['acc']<=1) & (~x['Y']) & (x['sup']<=off_med) & (x['loc']<=15)].copy()
    c['sup_v']=x['sup']; c['acc_v']=x['acc']; c['tri_v']=x['tri']; c['loc_v']=x['loc']
    c = c.sort_values('sup_v')
    blind[f]=c
    print(f"\n  ── {f} (지정지 {x['sup_name']} 중앙값 {off_med:.1f}) → 사각지대 {len(c)}곳 ──")
    print(c[['name','sup_v','acc_v','tri_v','loc_v','pop']].to_string(index=False,
        header=['지역','공급','접근성취약%','TRI%','관내이용률%','인구']))
# 투석: 공급 컬럼 부재 → 거리통과 ∧ 관내이용률≤15 ∧ 미지정 (+기관정보로 보강 예정)
x=F['투석']
c = d[(x['acc']<=1) & (~x['Y']) & (x['loc']<=15)].copy()
c['acc_v']=x['acc']; c['tri_v']=x['tri']; c['loc_v']=x['loc']
blind['투석'] = c.sort_values('loc_v')
print(f"\n  ── 투석 (공급 컬럼 부재 → 2중 기준) → 후보 {len(c)}곳 ──")
print(blind['투석'][['name','acc_v','tri_v','loc_v','pop']].head(12).to_string(index=False,
    header=['지역','접근성취약%','TRI%','관내이용률%','인구']))
# 응급: 거리통과(양 기준 미달) ∧ 공급≤지정지중앙값 ∧ 관내이용률≤25 ∧ 미지정
off_em = EM['sup'][EM['Y']].median()
c = d[(d['a30']<27) & (d['a60']<27) & (~EM['Y']) & (EM['sup']<=off_em) & (EM['loc']<=25)].copy()
c['loc_v']=EM['loc']; c['sup_v']=EM['sup']
blind['응급'] = c.sort_values('loc_v')
print(f"\n  ── 응급 (지정지 {EM['sup_name']} 중앙값 {off_em:.2f}, 관내이용률≤25) → 후보 {len(c)}곳 ──")
print(blind['응급'][['name','sup_v','a30','a60','loc_v','pop']].head(15).to_string(index=False,
    header=['지역','기관/100km²','30분취약%','60분취약%','응급실관내%','인구']))

# [D] 민감도 스윕 ----------------------------------------------------------
SEC("[D] 유형II 임계값 민감도 (소아: 전문의 s × 관내이용률 l → 신규 지정 수 / 핵심5곳 포착)")
x=F['소아']
core5 = ['예산군','함안군','장성군','증평군','담양군']
print("       l=10   l=15   l=20   l=25")
for s_th in [4.0,4.5,5.0,5.4,6.0,6.5,7.0]:
    row=[]
    for l_th in [10,15,20,25]:
        sel = d[(x['sup']<=s_th) & (x['loc']<=l_th) & (~x['Y'])]
        hit = sel['시군구명'].isin(core5).sum()
        row.append(f"{len(sel):3d}({hit}/5)")
    print(f"  s={s_th:>3}: " + "  ".join(row))
print("  ※ 괄호는 핵심 5곳 포착 수. 채택안 [s=5.4, l=15] 주변의 안정성 확인용")

# [E] 소아 오탐 2곳 --------------------------------------------------------
SEC("[E] 소아 '오탐' 2곳 (규칙상 지정 대상인데 미지정) — 원인 조사")
x=F['소아']
fp2 = d[(x['acc']>=30) & (x['tri']<30) & (~x['Y'])]
cols_chk = ['name','pop']
for _,r in fp2.iterrows():
    i=r.name
    print(f"  {r['name']}: 접근성취약 {x['acc'][i]:.2f} / TRI {x['tri'][i]:.2f} / "
          f"전문의 {x['sup'][i]:.2f} / 관내이용률 {x['loc'][i]:.2f} / 인구 {d['pop'][i]:,.0f}")
    # 다른 분야 지정 여부
    print(f"    타 분야 지정: 분만={d['분만_A취약지'][i]} 투석={d['인공신장실_취약지'][i]} 응급={d['응급_취약지'][i]}")
# 응급 누락 1곳도
miss_em = d[(~((d['a30']>=27)|(d['a60']>=27))) & EM['Y']]
fp_em   = d[((d['a30']>=27)|(d['a60']>=27)) & ~EM['Y']]
for lab,dd in [('응급 누락(지정인데 규칙 미충족)',miss_em),('응급 오탐(규칙 충족인데 미지정)',fp_em)]:
    for _,r in dd.iterrows():
        i=r.name
        print(f"  [{lab}] {r['name']}: 30분 {d['a30'][i]:.2f} / 60분 {d['a60'][i]:.2f} / 인구 {d['pop'][i]:,.0f}")

# [F] OD 요양종별 — 동급 유출 분리 ----------------------------------------
SEC("[F] 핵심 5곳 — 요양종별 OD로 '동급(의원·병원·종합병원) 유출' 분리 (중증 상급 이송과 구분)")
od = rd("유출입_요양종별.csv")
core5_codes = d[d['시군구명'].isin(core5) & d['name'].str.contains('충남|경남|전남|충북')].copy()
name_map = dict(zip(core5_codes['시군구명'], core5_codes['name']))
tiers = {'동급(의원+병원+종합병원)':['의원','병원','종합병원'], '상급종합병원':['상급종합병원']}
for nm in core5:
    keys = [k for k in od['지역2'].astype(str).unique() if nm in k]
    if not keys: print(f"  {nm}: OD 키 미발견"); continue
    k = keys[0]
    line=[f"  {name_map.get(nm,nm):14s}"]
    for lab, ts in tiers.items():
        sub = od[(od['지역2']==k) & (od['중분류'].isin(ts))]
        tot = sub['입원건수'].sum()
        intra = sub[sub['지역1']==k]['입원건수'].sum()
        pct = 100*(1-intra/tot) if tot else float('nan')
        line.append(f"{lab}: 유출 {pct:5.1f}% ({tot:,.0f}건)")
    print("  |  ".join(line))
print("  ※ 참고: 요양종별 OD는 전 진료과 합산(소아 한정 아님). 동급 유출이 높으면 '중증 이송' 반론 통제")
# 전국 동급 유출 중앙값
sub_all = od[od['중분류'].isin(['의원','병원','종합병원'])]
tot_all = sub_all.groupby('지역2')['입원건수'].sum()
intra_all = sub_all[sub_all['지역1']==sub_all['지역2']].groupby('지역2')['입원건수'].sum()
out_all = (1-intra_all.reindex(tot_all.index).fillna(0)/tot_all)*100
print(f"  전국 동급 유출률 중앙값: {out_all.median():.1f}%")

# [G] 로지스틱 -------------------------------------------------------------
SEC("[G] 로지스틱 5-fold CV — 공급 변수 무관성 (소아·분만)")
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
cv = StratifiedKFold(5, shuffle=True, random_state=42)
for f in ['소아','분만']:
    x=F[f]; y=x['Y'].astype(int)
    Xb = pd.DataFrame({'acc':x['acc'],'tri':x['tri']}).fillna(0)
    Xf = pd.DataFrame({'acc':x['acc'],'tri':x['tri'],'sup':x['sup'],'loc':x['loc']}).fillna(0)
    for lab,X in [('2변수',Xb),('4변수',Xf)]:
        pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
        auc = cross_val_score(pipe, X, y, cv=cv, scoring='roc_auc')
        pipe.fit(X,y)
        co = dict(zip(X.columns, pipe[-1].coef_[0].round(2)))
        print(f"  {f} [{lab}] CV AUC={auc.mean():.4f}(±{auc.std():.4f})  계수={co}")

# [H] 이중 트랙 최종 + 차상위 ---------------------------------------------
SEC("[H] 이중 트랙 최종안 — 유형II [공급≤지정지중앙값 ∧ 관내이용률≤15] 4분야 적용")
for f in ['소아','분만']:
    x=F[f]; off_med = x['sup'][x['Y']].median()
    t2 = d[(x['sup']<=off_med) & (x['loc']<=15) & (~x['Y'])]
    ov = d[(x['sup']<=off_med) & (x['loc']<=15) & (x['Y'])]
    print(f"  {f}: 유형II 신규 {len(t2)}곳 (기존 지정과 중복 {len(ov)}곳) → {sorted(t2['name'].tolist())}")
# 보상형 실패 재현(소아, 요약)
x=F['소아']
z = lambda s:(s-s.mean())/s.std()
idx = ( z(x['acc'].fillna(0)) + z(100-x['tri'].fillna(100))
      + z(-x['sup'].fillna(x['sup'].median())) + z(100-x['loc'].fillna(100)) )/4
top38 = d.assign(idx=idx).nlargest(38,'idx')
hit5 = top38['시군구명'].isin(core5).sum()
print(f"\n  보상형 합산 지수(소아, 상위38): 현행 유지 {int(top38[x['Y']].shape[0] if False else (top38.index.isin(d[x['Y']].index)).sum())}/18, 핵심5곳 포착 {hit5}/5  ← 기각 근거")
sub2 = top38[~top38.index.isin(d[x['Y']].index) & ~top38['시군구명'].isin(core5)]
print(f"  차상위 준취약지(지수 상위·미지정·비핵심): {len(sub2)}곳 — {sorted(sub2['name'].tolist())[:21]}")

with open(LOG,'w',encoding='utf-8') as fp: fp.write('\n'.join(_buf))
_orig_print(f"\n[로그 저장] {LOG}")
