# -*- coding: utf-8 -*-
"""
결과보고서 PDF 후처리 — 목차 페이지 삽입 · 페이지 번호 · PDF 북마크

Edge headless 로 렌더한 PDF를 받아서:
  1) md의 ## / ### 제목 위치를 PDF 본문에서 찾아 목차를 구성
  2) 표지 다음에 목차 페이지를 삽입 (본문 쪽 번호는 +1 보정)
  3) 표지·목차를 제외한 모든 쪽에 페이지 번호와 러닝 푸터를 찍음
  4) 같은 정보로 PDF 북마크(사이드바 목차)를 생성

사용법: python 보고서PDF_후처리.py <입력.pdf> <출력.pdf> <md경로>
"""
import io, os, re, sys
import pymupdf

if (sys.stdout.encoding or '').lower() not in ('utf-8', 'utf8'):   # 중복 래핑 방지
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FONT_R = r'C:\Windows\Fonts\malgun.ttf'
FONT_B = r'C:\Windows\Fonts\malgunbd.ttf'
INK, MUT, LINE, ACC = (0.10, 0.14, 0.20), (0.48, 0.53, 0.60), (0.88, 0.90, 0.93), (1.0, 0.478, 0.35)


def headings_from_md(md_path):
    """(레벨, 제목) 목록 — 표지/요약 이후의 ## 와 ### 만"""
    out = []
    for line in open(md_path, encoding='utf-8').read().split('\n'):
        m = re.match(r'^(#{2,3})\s+(.*?)\s*$', line)
        if not m:
            continue
        lvl, title = len(m.group(1)), m.group(2)
        if title.startswith('—'):          # 표지 부제
            continue
        out.append((lvl, title))
    return out


def find_page(doc, title, start=0):
    """제목 텍스트가 처음 나타나는 쪽 (0-based). 못 찾으면 None"""
    probe = re.sub(r'\s+', ' ', title).strip()
    for cut in (probe, probe[:24], probe[:14]):
        if len(cut) < 4:
            break
        for pno in range(start, len(doc)):
            if doc[pno].search_for(cut):
                return pno
    return None


def build_toc(doc, headings):
    """[(레벨, 제목, 원본쪽)] — 본문에서 찾은 것만"""
    toc, cursor = [], 0
    for lvl, title in headings:
        pno = find_page(doc, title, cursor)
        if pno is None:
            continue
        cursor = pno
        toc.append((lvl, title, pno))
    return toc


FR = pymupdf.Font(fontfile=FONT_R)
FB = pymupdf.Font(fontfile=FONT_B)


def layout_toc(toc, h, offset):
    """목차 항목을 쪽 단위로 나눠 [(페이지별 항목목록)] 반환"""
    pages, cur, y = [], [], 100.0
    for lvl, title, pno in toc:
        step = 15.5 if lvl == 2 else 12.6
        gap = 5 if lvl == 2 else 0
        if y + gap + step > h - 58:
            pages.append(cur)
            cur, y = [], 100.0
        cur.append((lvl, title, pno, y + gap))
        y += gap + step
    if cur:
        pages.append(cur)
    return pages


def draw_toc_page(page, items, w, h, offset, first=True):
    ml, mr = 40, 40
    page.insert_font(fontname='KR', fontfile=FONT_R)
    page.insert_font(fontname='KRB', fontfile=FONT_B)
    if first:
        page.insert_text((ml, 62), '목차', fontname='KRB', fontsize=21, color=INK)
        page.draw_rect(pymupdf.Rect(ml, 72, ml + 46, 75), color=None, fill=ACC)

    for lvl, title, pno, y in items:
        is_sec = (lvl == 2)
        size = 10.4 if is_sec else 9.0
        x = ml if is_sec else ml + 14
        font, fobj = ('KRB', FB) if is_sec else ('KR', FR)
        color = INK if is_sec else MUT
        label = re.sub(r'\s+—.*$', '', title)          # 부제(— 뒤) 잘라 한 줄 유지
        label = label if len(label) <= 40 else label[:39] + '…'
        num = str(pno + 1 + offset)
        tw = fobj.text_length(label, fontsize=size)
        nw = FR.text_length(num, fontsize=size)
        page.insert_text((x, y), label, fontname=font, fontsize=size, color=color)
        page.insert_text((w - mr - nw, y), num, fontname='KR', fontsize=size, color=color)
        dot_from, dot_to = x + tw + 6, w - mr - nw - 6
        if dot_to > dot_from:
            page.draw_line(pymupdf.Point(dot_from, y - 2.5), pymupdf.Point(dot_to, y - 2.5),
                           color=LINE, width=0.6, dashes='[0.6 2.6] 0')


def stamp_footers(doc, skip, label='측정과 배분 사이 — 분만취약지 제도의 전 과정 데이터 감사'):
    total = len(doc)
    for pno in range(skip, total):
        page = doc[pno]
        w, h = page.rect.width, page.rect.height
        page.insert_font(fontname='KR', fontfile=FONT_R)
        page.draw_line(pymupdf.Point(40, h - 34), pymupdf.Point(w - 40, h - 34),
                       color=LINE, width=0.6)
        page.insert_text((40, h - 24), label, fontname='KR', fontsize=7.2, color=MUT)
        num = f'{pno + 1} / {total}'
        nw = FR.text_length(num, fontsize=8)
        page.insert_text((w - 40 - nw, h - 24), num, fontname='KR', fontsize=8, color=MUT)


def main(src, dst, md_path):
    doc = pymupdf.open(src)
    headings = headings_from_md(md_path)
    toc = build_toc(doc, headings)
    w, h = doc[0].rect.width, doc[0].rect.height

    # 목차 쪽수를 알아야 본문 쪽 번호가 확정되므로 한 번 시산 후 확정
    n_toc = len(layout_toc(toc, h, 1))
    pages = layout_toc(toc, h, n_toc)
    print(f'  목차 항목 {len(toc)}개 (제목 {len(headings)}개 중) · 목차 {len(pages)}쪽')

    for i, items in enumerate(pages):
        page = doc.new_page(pno=1 + i, width=w, height=h)   # 표지 바로 뒤
        draw_toc_page(page, items, w, h, offset=len(pages), first=(i == 0))

    skip = 1 + len(pages)
    stamp_footers(doc, skip=skip)
    doc.set_toc([[lvl - 1, title, pno + 1 + len(pages)] for lvl, title, pno in toc])

    doc.save(dst, garbage=3, deflate=True)
    print(f'  완성: {os.path.basename(dst)} — {len(doc)}쪽')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
