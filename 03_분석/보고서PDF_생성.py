# -*- coding: utf-8 -*-
"""md → 인쇄용 HTML 변환 (Edge --print-to-pdf 용)"""
import sys, io, os, markdown
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CSS = """
  @page { size: A4; margin: 16mm 15mm 17mm 15mm; }
  * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  body { font-family: 'Malgun Gothic','맑은 고딕',sans-serif; font-size: 9.6pt;
         line-height: 1.74; color: #26303C; word-break: keep-all; margin: 0; background: #fff; }

  /* 파트 배너: 흰 카드 + 코랄 그라데이션 사이드바 + 그림자 */
  h1 { font-size: 14.5pt; color: #14263C; background: linear-gradient(135deg,#F6F9FC,#EDF2F8);
       padding: 4.5mm 6mm 4.5mm 8mm; margin: 0 0 5mm 0; border-radius: 10px;
       border-left: 5px solid #FF7A59; box-shadow: 0 2px 10px rgba(20,38,60,.10);
       page-break-before: always; page-break-after: avoid; letter-spacing: -.2px; }

  /* 표지(첫 h1 + 부제) */
  h1:first-of-type { page-break-before: avoid; font-size: 24pt; background: linear-gradient(135deg,#101B2E,#1B3050);
       color: #fff; padding: 12mm 9mm 5mm; margin: 0 0 0; border-radius: 14px 14px 0 0;
       border-left: none; box-shadow: none; }
  h1:first-of-type + h2 { font-size: 12.5pt; color: #FFC98A; font-weight: 600;
       background: linear-gradient(135deg,#101B2E,#1B3050); margin: 0 0 7mm; padding: 0 9mm 10mm;
       border-radius: 0 0 14px 14px; border: none; box-shadow: 0 4px 14px rgba(16,27,46,.28); }
  h1:first-of-type + h2::after { content: ''; display: block; width: 42mm; height: 1.6mm;
       background: linear-gradient(90deg,#FF7A59,#FFB86B); border-radius: 1mm; margin-top: 6mm; }

  h2 { font-size: 12.5pt; color: #14263C; margin: 8mm 0 3mm; padding: 0; border: none;
       page-break-after: avoid; letter-spacing: -.2px; }
  h2::after { content: ''; display: block; width: 16mm; height: 1.1mm; border-radius: 1mm;
       background: linear-gradient(90deg,#FF7A59,#FFB86B); margin-top: 1.6mm; }
  h3 { font-size: 10.8pt; color: #1B3E63; margin: 6mm 0 2mm; page-break-after: avoid; }
  h3::before { content: '◆'; color: #FF8A63; font-size: 7pt; margin-right: 1.6mm; vertical-align: 1px; }

  p { margin: 1.6mm 0; }
  ul, ol { margin: 1.5mm 0 2.5mm; padding-left: 6mm; }
  li { margin: .8mm 0; }
  li::marker { color: #FF7A59; }
  strong { color: #12314F; }
  code { font-family: Consolas,'Malgun Gothic',monospace; font-size: 8.8pt;
         background: #F0F4F9; color: #1B3E63; padding: 0 .38em; border-radius: 3px; }
  pre { font-family: Consolas,'Malgun Gothic',monospace; font-size: 8.9pt;
        background: linear-gradient(135deg,#101B2E,#16263E); color: #E8EEF5; border-radius: 8px;
        padding: 4mm 5.5mm; line-height: 1.85; page-break-inside: avoid; overflow: hidden;
        box-shadow: 0 2px 8px rgba(16,27,46,.18); }
  pre code { background: none; color: inherit; padding: 0; }

  table { border-collapse: separate; border-spacing: 0; width: 100%; margin: 3mm 0 4mm;
          font-size: 8.7pt; page-break-inside: avoid; border-radius: 8px; overflow: hidden;
          box-shadow: 0 1.5px 7px rgba(20,38,60,.10); }
  th, td { border: none; border-bottom: .5pt solid #E3E9F0; padding: 1.6mm 2.4mm;
           vertical-align: top; text-align: left; }
  th { background: linear-gradient(135deg,#1B3050,#254264); color: #FFD9B0; font-weight: 700; }
  tr:nth-child(even) td { background: #F6F9FC; }
  tr:nth-child(odd) td { background: #FFFFFF; }
  tr:last-child td { border-bottom: none; }

  blockquote { margin: 3.5mm 0; padding: 3mm 5mm; border: none; border-radius: 8px;
               background: linear-gradient(135deg,#FFF4EE,#FFF9F3);
               box-shadow: 0 1.5px 6px rgba(232,93,66,.12); page-break-inside: avoid;
               border-left: 4px solid #FF8A63; }
  blockquote p { margin: 1mm 0; }
  hr { border: none; height: 1mm; border-radius: .5mm; margin: 5mm 0;
       background: linear-gradient(90deg,#FF7A59,#FFB86B,transparent); }
  img { display: block; max-width: 90%; max-height: 172mm; margin: 4.5mm auto;
        page-break-inside: avoid; border-radius: 8px; padding: 2mm; background: #fff;
        box-shadow: 0 2.5px 10px rgba(20,38,60,.14); }
"""

def convert(md_path, html_path, title):
    src = open(md_path, encoding='utf-8').read()
    body = markdown.markdown(src, extensions=['tables','fenced_code','sane_lists'])
    html = (f'<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">'
            f'<title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>')
    open(html_path, 'w', encoding='utf-8').write(html)
    print(f"OK {html_path} ({len(html)} chars)")

if __name__ == '__main__':
    convert(sys.argv[1], sys.argv[2], sys.argv[3])
