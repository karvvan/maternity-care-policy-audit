# -*- coding: utf-8 -*-
"""
결과보고서 빌드 — md 하나에서 최종 인쇄용 PDF까지 한 번에

  04_제출물/결과보고서_v2_통합.md
      → (보고서PDF_생성) 잡지형 HTML
      → (Edge headless) PDF
      → (보고서PDF_후처리) 목차·쪽번호·북마크
      → 04_제출물/결과보고서_v2_통합.pdf

사용법:  python 보고서_빌드.py
PDF가 뷰어에 열려 있어 교체가 막히면 임시 파일 경로를 안내하고 종료한다.
"""
import io, os, shutil, subprocess, sys, tempfile

if (sys.stdout.encoding or '').lower() not in ('utf-8', 'utf8'):   # 중복 래핑 방지
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import 보고서PDF_생성 as gen
import 보고서PDF_후처리 as post

BASE = gen.BASE
MD = os.path.join(BASE, '04_제출물', '결과보고서_v2_통합.md')
OUT = os.path.join(BASE, '04_제출물', '결과보고서_v2_통합.pdf')
TITLE = '결과보고서 — 분만취약지 제도의 전 과정 데이터 감사'

EDGE_CANDIDATES = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
]


def find_edge():
    for p in EDGE_CANDIDATES:
        if os.path.exists(p):
            return p
    raise RuntimeError('Microsoft Edge를 찾지 못했습니다')


def main():
    work = tempfile.mkdtemp(prefix='report_build_')
    html = os.path.join(work, 'report.html')
    raw = os.path.join(work, 'raw.pdf')
    final = os.path.join(work, 'final.pdf')

    print('[1/3] 마크다운 → 잡지형 HTML')
    gen.convert(MD, html, TITLE)

    print('[2/3] HTML → PDF (Edge headless)')
    subprocess.run([find_edge(), '--headless', '--disable-gpu', '--no-pdf-header-footer',
                    f'--print-to-pdf={raw}', 'file:///' + html.replace('\\', '/')],
                   check=True, capture_output=True)

    print('[3/3] 목차·쪽번호·북마크 후처리')
    post.main(raw, final, MD)

    try:
        shutil.copyfile(final, OUT)
        print(f'\n완료 → {OUT}')
    except PermissionError:
        print(f'\n!! PDF가 열려 있어 교체하지 못했습니다. 뷰어를 닫고 아래 파일을 복사하세요:\n   {final}')
        return 1
    shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
