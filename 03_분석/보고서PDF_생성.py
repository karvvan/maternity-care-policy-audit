# -*- coding: utf-8 -*-
"""
결과보고서 md → 잡지형 인쇄 PDF용 HTML 생성기

디자인 언어 (화이트 테마):
  · 순백 배경, 모든 도형·표·사진의 그림자는 오른쪽-아래로 (원근 통일)
  · 표는 무채색 (차콜 헤더 + 회색 라인 + 지브라)
  · 부(部) 배너는 파트별 액센트 컬러 로테이션 + 3D 구체 장식
  · 실사 사진(위키미디어 커먼즈)·자료화면(정부 지침 실물 페이지)·삽화(지도·아이콘) 배치

사용법:
  python 보고서PDF_생성.py <md> <html> <title>
  이후 Edge headless --print-to-pdf 로 PDF 변환.
자산 경로: ASSET_DIR(디자인 에셋 캐시), PHOTO_DIR(기본 05_팀운영/보고서_사진소스)
"""
import sys, io, os, re, markdown

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTO = os.environ.get('PHOTO_DIR') or os.path.join(BASE, '05_팀운영', '보고서_사진소스')

import design_assets
ASSETS = design_assets.build_defaults()


def uri(p):
    return 'file:///' + p.replace('\\', '/')


CSS = f"""
  @page {{ size: A4; margin: 15mm 14mm 16mm 14mm; }}
  * {{ box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  body {{ font-family: 'Malgun Gothic','맑은 고딕',sans-serif; font-size: 9.6pt;
         line-height: 1.74; color: #262B33; word-break: keep-all; margin: 0; background: #fff; }}

  /* ── 표지 ── */
  .cover {{ position: relative; height: 258mm; overflow: hidden; page-break-after: always; }}
  .cover .blob {{ position: absolute; }}
  .cover .map {{ position: absolute; right: 2mm; top: 40mm; width: 86mm; }}
  .cover .pin {{ position: absolute; right: 52mm; top: 52mm; width: 13mm; }}
  .cover .sph {{ position: absolute; }}
  .cover .chip {{ position: absolute; left: 2mm; top: 52mm; width: 13mm; height: 3.4mm;
                 border-radius: 2mm; background: linear-gradient(90deg,#FF7A59,#FFB86B);
                 box-shadow: 2mm 2.5mm 5mm rgba(200,80,45,.30); }}
  .cover .label {{ position: absolute; left: 2mm; top: 60mm; font-size: 12pt; color: #6A7B92; }}
  .cover h1.t {{ position: absolute; left: 2mm; top: 68mm; font-size: 37pt; margin: 0;
                color: #1A2434; letter-spacing: -1px; }}
  .cover .sub {{ position: absolute; left: 2mm; top: 90mm; font-size: 13.5pt; color: #17456B;
                width: 100mm; line-height: 1.55; }}
  .cover .bar {{ position: absolute; left: 2mm; top: 112mm; width: 72mm; }}
  .cover .meta {{ position: absolute; left: 2mm; top: 122mm; width: 96mm; background: #fff;
                 border: 0.4mm solid #E4EAF2; border-radius: 3.5mm; padding: 6mm 7mm;
                 box-shadow: 2.2mm 2.8mm 7mm rgba(30,42,62,.14); }}
  .cover .meta b {{ color: #1A2434; }}
  .cover .meta div {{ margin: 1.2mm 0; font-size: 10pt; color: #4A5768; }}
  .cover .foot {{ position: absolute; left: 2mm; bottom: 6mm; font-size: 9.5pt; color: #9AA7B8; }}

  /* ── 부 배너: 파트별 액센트 로테이션 + 구체 장식 ── */
  h1 {{ font-size: 14.5pt; color: #1A2434; padding: 5mm 24mm 5mm 8mm; margin: 0 0 5.5mm 0;
       border-radius: 3mm; background: #fff url('{uri(ASSETS["sphere_coral"])}') no-repeat
       right 5mm center / 14mm; border: 0.4mm solid #E9EDF3; border-left: 1.6mm solid #FF7A59;
       box-shadow: 2mm 2.6mm 6.5mm rgba(30,42,62,.13);
       page-break-before: always; page-break-after: avoid; letter-spacing: -.2px; }}
  h1:nth-of-type(3) {{ border-left-color: #3E6DB5;
       background-image: url('{uri(ASSETS["sphere_blue"])}'); }}
  h1:nth-of-type(4) {{ border-left-color: #149E8C;
       background-image: url('{uri(ASSETS["sphere_teal"])}'); }}
  h1:nth-of-type(5) {{ border-left-color: #E8882E;
       background-image: url('{uri(ASSETS["ring_coral"])}'); }}
  .cover h1.t {{ background: none; border: none; box-shadow: none; padding: 0;
       page-break-before: avoid; font-size: 37pt; }}

  h2 {{ font-size: 12.5pt; color: #1A2434; margin: 8mm 0 3mm; padding: 0; border: none;
       page-break-after: avoid; letter-spacing: -.2px; }}
  h2::after {{ content: ''; display: block; width: 16mm; height: 1.1mm; border-radius: 1mm;
       background: linear-gradient(90deg,#FF7A59,#FFB86B); margin-top: 1.6mm; }}
  h3 {{ font-size: 10.8pt; color: #253A55; margin: 6mm 0 2mm; page-break-after: avoid; }}
  h3::before {{ content: '◆'; color: #FF8A63; font-size: 7pt; margin-right: 1.6mm; vertical-align: 1px; }}

  p {{ margin: 1.6mm 0; }}
  ul, ol {{ margin: 1.5mm 0 2.5mm; padding-left: 6mm; }}
  li {{ margin: .8mm 0; }}
  li::marker {{ color: #FF7A59; }}
  strong {{ color: #16233A; }}
  code {{ font-family: Consolas,'Malgun Gothic',monospace; font-size: 8.8pt;
         background: #F1F3F6; color: #333A44; padding: 0 .38em; border-radius: 3px; }}
  pre {{ font-family: Consolas,'Malgun Gothic',monospace; font-size: 8.9pt;
        background: #2B313A; color: #E8EEF5; border-radius: 3mm;
        padding: 4mm 5.5mm; line-height: 1.85; page-break-inside: avoid; overflow: hidden;
        box-shadow: 1.8mm 2.4mm 6mm rgba(30,42,62,.20); }}
  pre code {{ background: none; color: inherit; padding: 0; }}

  /* ── 표: 무채색 ── */
  table {{ border-collapse: separate; border-spacing: 0; width: 100%; margin: 3mm 0 4.5mm;
          font-size: 8.7pt; page-break-inside: avoid; border-radius: 2.5mm; overflow: hidden;
          box-shadow: 1.8mm 2.4mm 6mm rgba(30,42,62,.13); border: 0.35mm solid #E2E6EC; }}
  th, td {{ border: none; border-bottom: .4mm solid #E7EAEF; padding: 1.7mm 2.5mm;
           vertical-align: top; text-align: left; }}
  th {{ background: #33393F; color: #FFFFFF; font-weight: 700; letter-spacing: .2px; }}
  tr:nth-child(even) td {{ background: #F6F7F9; }}
  tr:nth-child(odd) td {{ background: #FFFFFF; }}
  tr:last-child td {{ border-bottom: none; }}

  blockquote {{ margin: 3.5mm 0; padding: 3mm 5mm; border: 0.4mm solid #F0E2D8; border-radius: 2.5mm;
               background: #FFF9F4; box-shadow: 1.6mm 2.2mm 5.5mm rgba(180,110,70,.13);
               page-break-inside: avoid; border-left: 1.5mm solid #FF8A63; }}
  blockquote p {{ margin: 1mm 0; }}
  hr {{ border: none; height: 1mm; border-radius: .5mm; margin: 5mm 0;
       background: linear-gradient(90deg,#FF7A59,#FFB86B,transparent); }}

  /* ── 그림·사진 ── */
  figure {{ margin: 4.5mm auto; page-break-inside: avoid; text-align: center; }}
  figure img {{ max-width: 90%; max-height: 168mm; border-radius: 2.5mm; padding: 1.6mm;
               background: #fff; border: 0.35mm solid #E7EAEF;
               box-shadow: 2mm 2.8mm 7mm rgba(30,42,62,.15); }}
  figcaption {{ font-size: 8.3pt; color: #7A8698; margin-top: 1.6mm; }}

  .photo {{ page-break-inside: avoid; margin: 2mm 0 3mm; }}
  .photo img {{ width: 100%; border-radius: 3mm; box-shadow: 2.2mm 3mm 7mm rgba(30,42,62,.22);
               display: block; }}
  .photo .cap {{ font-size: 8pt; color: #8A96A6; margin-top: 1.4mm; line-height: 1.4; }}
  .pr {{ float: right; width: 58mm; margin: 1mm 0 3mm 5mm; }}
  .pl {{ float: left; width: 54mm; margin: 1mm 5mm 3mm 0; }}
  .shot img {{ border: 0.5mm solid #E2E6EC; padding: 1mm; background: #fff; }}

  .clear {{ clear: both; }}
"""

COVER = f"""
<div class="cover">
  <img class="blob" src="{uri(ASSETS['blob_coral'])}" style="right:-58mm; top:-62mm; width:150mm;">
  <img class="blob" src="{uri(ASSETS['blob_blue'])}" style="left:-70mm; bottom:-60mm; width:160mm;">
  <img class="blob" src="{uri(ASSETS['blob_teal'])}" style="left:52mm; bottom:-38mm; width:90mm;">
  <img class="map" src="{uri(ASSETS['korea_map'])}">
  <img class="pin" src="{uri(ASSETS['icon_pin'])}">
  <img class="sph" src="{uri(ASSETS['sphere_coral'])}" style="right:78mm; bottom:44mm; width:34mm;">
  <img class="sph" src="{uri(ASSETS['ring_blue'])}" style="right:6mm; bottom:26mm; width:34mm;">
  <img class="sph" src="{uri(ASSETS['sphere_teal'])}" style="right:86mm; top:30mm; width:14mm;">
  <div class="chip"></div>
  <div class="label">데이터 분석 결과보고서</div>
  <h1 class="t">측정과 배분 사이</h1>
  <div class="sub">— 분만취약지 제도의 전 과정 데이터 감사와 우선순위 모형</div>
  <img class="bar" src="{uri(ASSETS['glow_bar'])}">
  <div class="meta">
    <div><b>2026 제5회 명지대학교 창의적 SW프로그램 경진대회</b> · 빅데이터 분석 부문</div>
    <div>결과보고서 v2 통합본 · 2026-08-10</div>
    <div>데이터: 헬스맵 공공 데이터셋 9종(226만 행) + 복지부 공고·지침 — 전량 공개 자료</div>
    <div>전 수치 독립 재실행 검증 완료 · 소스/데이터 전체 동봉</div>
  </div>
  <div class="foot">정부는 분만취약지를 정밀하게 측정한다. 그러나 지정 규칙은 이동시간만 보고, 배분은 그 측정값조차 따르지 않는다.</div>
</div>
"""


def photo_fig(fname, cap, cls='pr', shot=False):
    p = os.path.join(PHOTO, fname)
    return (f'<div class="photo {cls}{" shot" if shot else ""}"><img src="{uri(p)}">'
            f'<div class="cap">{cap}</div></div>')


INJECT = [
    (r'(<h2>1\. 서론</h2>)',
     photo_fig('newborn.jpg', '분만 인프라는 한 명의 탄생을 받치는 지역의 기반 시설이다. '
               '(사진: Wikimedia Commons, Shixart1985, CC BY 2.0)', 'pr')),
    (r'(<h2>2\. 제도와 이론</h2>)',
     photo_fig('gov_cover.png', '자료화면 — 보건복지부 「2026년 분만취약지 지원사업 안내」(343쪽) 표지. '
               '본 연구의 모든 임계값·절차는 이 문서에서 나온다.', 'pr', shot=True)),
    (r'(<h3>5\.3\.[^<]*</h3>)',
     photo_fig('village.jpg', '거리 기준을 통과해도 관내 분만 인프라가 소멸한 농촌 지역이 실재한다. '
               '(사진: Wikimedia Commons, Alain Seguin, CC BY-SA 3.0)', 'pr')),
    (r'(<h3>5\.4\.[^<]*</h3>)',
     photo_fig('pregnant.jpg', '분만은 하루의 이벤트가 아니라 산전진찰 10여 회를 포함한 9개월의 과정이다. '
               '(사진: Joey Thompson, Unsplash/CC0)', 'pl')),
    (r'(<h2>7\. 처방[^<]*</h2>)',
     photo_fig('gov_criteria.png', '자료화면 — 지침 p.21, 배경인구 36,588명 기준 원문. '
               '본 연구는 이 값의 적용 인구(가임/총인구)를 검증해 §7에 공개한다.', 'pr', shot=True)),
]

CREDIT_NOTE = ('<p><strong>사진·자료화면 출처</strong>: Wikimedia Commons(Shixart1985 CC BY 2.0 · '
               'Alain Seguin CC BY-SA 3.0 · Joey Thompson CC0), 보건복지부 지침(공공저작물). '
               '자료화면은 출처 명시 후 인용 목적으로 사용.</p>')


def convert(md_path, html_path, title):
    src = open(md_path, encoding='utf-8').read()
    body = markdown.markdown(src, extensions=['tables', 'fenced_code', 'sane_lists'])

    # 1) 원래 타이틀(h1+h2+메타 문단)을 히어로 커버로 대체
    body = re.sub(r'^<h1>.*?</h1>\s*<h2>.*?</h2>\s*<p>.*?</p>', COVER, body, count=1, flags=re.S)

    # 1.5) md의 상대경로 그림을 절대 file:// 경로로 재작성 (HTML 위치와 무관하게 동작)
    fig_dir = uri(os.path.join(BASE, '04_제출물', '그림'))
    body = body.replace('src="그림/', f'src="{fig_dir}/')

    # 2) 이미지 → figure/figcaption
    body = re.sub(r'<p><img alt="([^"]*)" src="([^"]*)"\s*/?>(</p>)',
                  r'<figure><img alt="\1" src="\2"><figcaption>\1</figcaption></figure>', body)

    # 3) 사진·자료화면 주입
    for pat, html in INJECT:
        body, n = re.subn(pat, lambda m, h=html: m.group(1) + h, body, count=1)
        if n == 0:
            print(f'  !! 앵커 미발견: {pat[:40]}')

    # 4) 사진 출처를 데이터 윤리 절에 추가
    body = body.replace('공공누리 출처 표기.</p>', '공공누리 출처 표기.</p>' + CREDIT_NOTE)

    # 5) 부 배너 앞 float 잔여 정리
    body = re.sub(r'(<h1>)', r'<div class="clear"></div>\1', body)

    html = (f'<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">'
            f'<title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>')
    open(html_path, 'w', encoding='utf-8').write(html)
    print(f'OK {html_path} ({len(html)} chars)')


if __name__ == '__main__':
    convert(sys.argv[1], sys.argv[2], sys.argv[3])
