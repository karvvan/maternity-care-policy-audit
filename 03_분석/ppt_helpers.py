# -*- coding: utf-8 -*-
"""계획서/결과보고서 PPT 공용 헬퍼 (16:9, 네이비 테마)"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

NAVY = RGBColor(0x17, 0x45, 0x6B)
DARK = RGBColor(0x0F, 0x2B, 0x44)
RED = RGBColor(0xC0, 0x39, 0x2B)
GRAY = RGBColor(0x55, 0x5F, 0x6B)
LIGHT = RGBColor(0xF2, 0xF6, 0xFA)
LINE = RGBColor(0xB9, 0xC4, 0xCF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
REDBG = RGBColor(0xFB, 0xF0, 0xEE)
FONT = '맑은 고딕'


def new_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs, prs.slide_layouts[6]


def set_font(run, size, bold=False, color=DARK):
    f = run.font
    f.size, f.bold, f.name = Pt(size), bold, FONT
    f.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {})
        rPr.append(ea)
    ea.set('typeface', FONT)


def text_block(slide, x, y, w, h, items, anchor=MSO_ANCHOR.TOP):
    """items: (텍스트, 크기, 굵게, 색, 단락 뒤 간격pt). '• ' 시작 단락은 내어쓰기."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, (t, size, bold, color, after) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(after)
        p.line_spacing = 1.12
        r = p.add_run(); r.text = t
        set_font(r, size, bold, color)
        if t.startswith('• '):
            pPr = p._p.get_or_add_pPr()
            pPr.set('marL', '160020'); pPr.set('indent', '-160020')
    return tb


def rect(slide, x, y, w, h, fill, line_color=None):
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sp.adjustments[0] = 0.06
    sp.fill.solid(); sp.fill.fore_color.rgb = fill
    if line_color is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line_color; sp.line.width = Pt(1)
    sp.shadow.inherit = False
    return sp


def card(slide, x, y, w, h, title, body, fill=LIGHT, tcolor=NAVY, tsize=13, bsize=11.5):
    rect(slide, x, y, w, h, fill, LINE)
    items = [(title, tsize, True, tcolor, 3)]
    for line in body:
        items.append((line if line.startswith(('→', '—')) else '• ' + line, bsize, False, DARK, 2))
    text_block(slide, x + 0.15, y + 0.1, w - 0.3, h - 0.2, items)


def header(slide, no, title, footer_label, sub=None):
    rect(slide, 0, 0, 13.333, 0.92, NAVY)
    text_block(slide, 0.55, 0.13, 11.2, 0.7, [(title, 22, True, WHITE, 0)], anchor=MSO_ANCHOR.MIDDLE)
    text_block(slide, 12.35, 0.2, 0.8, 0.55, [(f'{no:02d}', 16, True, RGBColor(0x9F, 0xB8, 0xCC), 0)])
    if sub:
        text_block(slide, 0.55, 1.02, 12.3, 0.42, [(sub, 12.5, False, GRAY, 0)])
    text_block(slide, 0.55, 7.08, 12.3, 0.35,
               [(f'2026 제5회 명지대학교 창의적 SW프로그램 경진대회 · 빅데이터 분석 부문 — {footer_label}', 9, False, RGBColor(0x9A, 0xA5, 0xB1), 0)])


def table(slide, x, y, w, rows, widths=None, header_size=11.5, body_size=11, row_h=0.42,
          highlight_rows=(), highlight_color=None):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(row_h * len(rows)))
    tbl = shape.table
    if widths:
        for j, wd in enumerate(widths):
            tbl.columns[j].width = Inches(wd)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.margin_top = cell.margin_bottom = Emu(27432)
            cell.margin_left = cell.margin_right = Emu(64008)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.line_spacing = 1.05
            r = p.add_run(); r.text = val
            if i == 0:
                set_font(r, header_size, True, WHITE)
                cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
            elif i in highlight_rows:
                set_font(r, body_size, True, RED if highlight_color is None else highlight_color)
                cell.fill.solid(); cell.fill.fore_color.rgb = REDBG
            else:
                set_font(r, body_size, False, DARK)
                cell.fill.solid()
                cell.fill.fore_color.rgb = WHITE if i % 2 == 1 else RGBColor(0xF7, 0xFA, 0xFC)
    return tbl


def picture(slide, path, x, y, max_w, max_h):
    """비율 유지하며 (x,y) 기준 상자 안에 이미지 배치, 가운데 정렬."""
    from PIL import Image
    iw, ih = Image.open(path).size
    scale = min(max_w / iw, max_h / ih)
    w, h = iw * scale, ih * scale
    return slide.shapes.add_picture(path, Inches(x + (max_w - w) / 2), Inches(y + (max_h - h) / 2),
                                    Inches(w), Inches(h))
