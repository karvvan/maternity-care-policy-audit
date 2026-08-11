# -*- coding: utf-8 -*-
"""
시연 영상 생성 (5분 내외 mp4)

소재: 결과보고서 PPT 슬라이드(1920x1080 PNG) + edge-tts 한국어 나레이션
각 씬 = 슬라이드 1장 + 나레이션, 잔잔한 줌(Ken Burns) + 페이드 전환.
씬 길이는 나레이션 길이에 맞춰 자동 산정된다.

사용법:
  1) PowerPoint로 04_제출물/데이터분석_결과보고서.pptx 슬라이드를 1920x1080 PNG로
     내보내 SLIDES 폴더에 s01.png ~ s19.png 로 둔다.
  2) python 시연영상_생성.py  →  04_제출물/시연영상.mp4
"""
import asyncio, os, subprocess, sys, io, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLIDES = os.environ.get('SLIDES_DIR') or os.path.join(BASE, '_video_slides')
WORK = os.environ.get('VIDEO_WORK') or os.path.join(BASE, '_video_work')
OUT = os.path.join(BASE, '04_제출물', '시연영상.mp4')
VOICE = 'ko-KR-InJoonNeural'
RATE = '+6%'
os.makedirs(WORK, exist_ok=True)

# ── 대본: (슬라이드 파일, 나레이션) ─────────────────────────
SCENES = [
    ('s01.png',
     '2026 명지대학교 창의적 SW프로그램 경진대회, 빅데이터 분석 부문 출품작, "측정과 배분 사이"입니다. '
     '분만취약지 제도의 측정, 지정, 배분 전 과정을 정부 공개 데이터만으로 감사하고, 대안 우선순위 모형을 제시합니다.'),
    ('s03.png',
     '보건복지부의 분만취약지 정책은 측정, 지정, 배분의 세 단계로 작동합니다. 정부는 2년마다 전국 시군의 접근성과 '
     '의료이용률을 정밀하게 측정합니다. 그런데 저희는 두 가지를 의심했습니다. 지정은 이동시간 지표만으로 판정되고, '
     '배분에는 누구를 먼저 지원할지 줄 세우는 규칙이 없다는 것입니다. 그래서 취약지라는 현상이 아니라, '
     '취약지를 판정하고 지원하는 제도 그 자체를 분석 대상으로 삼았습니다.'),
    ('s06.png',
     '데이터는 국립중앙의료원 헬스맵 공공 데이터셋 9종, 약 226만 행과 복지부 공고, 그리고 343쪽의 정부 지침입니다. '
     '전량 공개 자료라 누구나 재현할 수 있습니다. 공고의 등급표를 직접 전사하고, 환자 유출입 자료로 관내 분만 수행량을, '
     '이용률로 미충족 분만 규모를 직접 구축했습니다. 재가공 수치는 공식 통계와 상관 0.999988로 일치했습니다.'),
    ('s08.png',
     '먼저 지정 단계입니다. 고시에 공표된 판정식을 그대로 재계산해 실제 지정과 대조한 결과, 159건 중 158건, '
     '99.4퍼센트가 재현됐습니다. 분만 분야는 29건 전부입니다. 공급 변수를 추가해도 판별력은 전혀 늘지 않았습니다. '
     '지정은 정말로 이동시간만 봅니다. 불일치 4건은 오류가 아니라, 지정과 해제가 데이터 기반으로 상시 갱신되지 '
     '않는다는 행정 시차의 증거였습니다.'),
    ('s09.png',
     '그렇다면 무엇이 걸러질까요. 거리 기준은 통과하지만 관내 공급이 소멸한 지역입니다. 분만에서는 의왕, 과천, '
     '경기 광주 등 다섯 곳이 어떤 등급 체계에도 없는 완전 사각이었고, 소아청소년과에서는 다섯 개 지역의 입원 '
     '5,689건 전량이 관외로 유출되고 있었습니다. 전남 장성군은 세 개 분야에서 동시에 이 패턴을 보입니다.'),
    ('s11.png',
     '다음은 배분 단계입니다. 실질 취약지 A, B 등급 53곳 중 21곳만 지원을 받았습니다. A등급의 지원 오즈는 '
     'B등급의 4.82배로 유의했지만, 다변량 분석 결과 그 선정은 공개 지표로 16퍼센트 남짓밖에 설명되지 않았습니다. '
     '배분을 결정하는 규칙은 데이터 바깥에 있었습니다.'),
    ('s13.png',
     '저희의 처방은 새 기준을 만들지 않는 것입니다. 정부 문서의 임계값만 조합해 우선순위 모형을 만들었습니다. '
     '취약이 가장 깊은 곳을 먼저 보는 심도 축과, 영향 인원이 큰 곳을 먼저 보는 부담 축. 두 순위의 상관은 '
     '마이너스 0.190으로, 서로 다른 지도를 그립니다. 저희는 이 둘을 평균 내지 않고 병렬로 제시합니다.'),
    ('s14.png',
     '규칙 기반 유형 배정의 결과, 분만실 설치 검토가 필요한 일곱 곳 중 여섯 곳이 미지원 상태였습니다. '
     '반면 완화책인 순회진료 권고 지역의 절반은 이미 지원을 받고 있었습니다.'),
    ('s15.png',
     '이 지도가 결론을 압축합니다. 심도 1위 청송, 5위 영덕, 9위 평창, 12위 의령, 13위 장수, 15위 신안. '
     '모형 최상위 여섯 곳이 전부 비어 있습니다. 반대로 심도 41위 함양, 44위 부여, 50위 함평은 지원을 받고 '
     '있습니다. 깊은 곳은 비어 있고, 얕은 곳이 채워져 있습니다.'),
    ('s17.png',
     '그래서 다섯 가지를 제언합니다. 공급 공백형 지정 트랙 신설, 이용률 지표의 관내외 병기, 우선순위에 부담 축 병기, '
     'B등급 공백형 별도 관리, 그리고 시도 선별용 표준 우선순위표 제공입니다. 배분 제언 세 가지는 예산 증액 없이 '
     '가능하며, 모든 임계값은 정부 자신의 문서에서 나옵니다.'),
    ('s18.png',
     '모든 수치는 원시 데이터에서 독립 재실행으로 검증했고, 전체 소스와 데이터는 깃 저장소로 버전 관리됩니다.'),
    ('s19.png',
     '현행 배분은 취약의 깊이를 반영합니다. 다만 그 취약을 겪는 인원의 규모는 반영하지 않습니다. '
     '저희는 정부 자신의 기준으로 그 축을 하나 추가했습니다. 감사합니다.'),
]

PAD_HEAD, PAD_TAIL, FADE = 0.6, 0.9, 0.5


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        raise RuntimeError(f'FAIL {" ".join(cmd[:6])}...\n{r.stderr[-1500:]}')
    return r


def probe_dur(path):
    r = run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', path])
    return float(json.loads(r.stdout)['format']['duration'])


async def synth_all():
    import edge_tts
    for i, (_, text) in enumerate(SCENES):
        mp3 = os.path.join(WORK, f'nar{i:02d}.mp3')
        if not os.path.exists(mp3):
            await edge_tts.Communicate(text, VOICE, rate=RATE).save(mp3)
            print(f'  나레이션 {i + 1}/{len(SCENES)}')


def build():
    asyncio.run(synth_all())
    parts, total = [], 0.0
    for i, (img, _) in enumerate(SCENES):
        mp3 = os.path.join(WORK, f'nar{i:02d}.mp3')
        dur = probe_dur(mp3) + PAD_HEAD + PAD_TAIL
        total += dur
        part = os.path.join(WORK, f'scene{i:02d}.mp4')
        parts.append(part)
        if os.path.exists(part) and abs(probe_dur(part) - dur) < 0.2:
            continue
        frames = int(dur * 30)
        step = 0.06 / frames    # 씬 길이와 무관하게 종료 시점 확대율 1.06배
        zoom = (f"zoompan=z='1+{step:.8f}*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                f":d={frames}:s=1920x1080:fps=30")
        vf = (f"scale=2880:1620,{zoom},"
              f"fade=t=in:st=0:d={FADE},fade=t=out:st={dur - FADE:.2f}:d={FADE},format=yuv420p")
        af = f"adelay={int(PAD_HEAD * 1000)}|{int(PAD_HEAD * 1000)},apad=pad_dur={PAD_TAIL}"
        run(['ffmpeg', '-y', '-loop', '1', '-i', os.path.join(SLIDES, img), '-i', mp3,
             '-filter_complex', f'[0:v]{vf}[v];[1:a]{af}[a]', '-map', '[v]', '-map', '[a]',
             '-t', f'{dur:.3f}', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
             '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', part])
        print(f'  씬 {i + 1}/{len(SCENES)} ({dur:.1f}s)')
    lst = os.path.join(WORK, 'concat.txt')
    with open(lst, 'w', encoding='utf-8') as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', OUT])
    m, s = divmod(probe_dur(OUT), 60)
    print(f'완성: {OUT} — {int(m)}분 {s:.0f}초, {os.path.getsize(OUT) / 1e6:.1f}MB')


if __name__ == '__main__':
    build()
