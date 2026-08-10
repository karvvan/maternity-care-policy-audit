# 무진님 업데이트

무진님 작업물을 올리는 폴더입니다. **이 폴더 안은 자유롭게 쓰셔도 됩니다.**
반대로 이 폴더 **밖은 읽기 전용**입니다 — 참고로 읽는 건 자유지만, 고치면 서로 작업이 꼬입니다.

## 처음 한 번만 (중요)

```bash
git clone https://github.com/karvvan/maternity-care-policy-audit.git
cd maternity-care-policy-audit
git config core.hooksPath .githooks
```

마지막 줄이 안전장치입니다. 실수로 `main`에 직접 올리거나, 남의 폴더를 고치거나,
원격 커밋을 지우는 push를 하면 **push가 자동으로 막힙니다.**

## 작업할 때마다

```bash
git pull                                # 최신 상태 받기
git checkout -b mujin/작업이름           # 자기 브랜치에서 작업
# "무진님 업데이트" 폴더에 파일 추가/수정
git add "무진님 업데이트"
git commit -m "무슨 작업을 했는지 한 줄"
git push -u origin mujin/작업이름
```

push하면 GitHub에 **Compare & pull request** 버튼이 뜹니다. 눌러서 PR을 만들어 주시면
확인 후 `main`에 합칩니다.

## 터미널 없이 웹으로 올리는 방법

아래 주소로 들어가 파일을 끌어다 놓으면 됩니다.

https://github.com/karvvan/maternity-care-policy-audit/upload/main/%EB%AC%B4%EC%A7%84%EB%8B%98%20%EC%97%85%EB%8D%B0%EC%9D%B4%ED%8A%B8

올린 뒤 아래쪽에서 **"Create a new branch for this commit and start a pull request"** 를
선택하고 **Propose changes** 를 눌러주세요.
(그 위의 *Commit directly to the main branch* 는 선택하지 말아주세요.)

## 하지 말아야 할 것

- `main` 브랜치에 직접 push
- `git push --force` / `--force-with-lease` — 상대 작업이 사라집니다
- `git push --no-verify` — 위 안전장치를 무력화합니다
- 이 폴더 밖의 파일 수정
