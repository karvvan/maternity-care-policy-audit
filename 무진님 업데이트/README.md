# 무진님 업데이트

무진님 작업물을 올리는 폴더입니다. 이 폴더 안은 자유롭게 쓰셔도 됩니다.

## 올리는 방법

```bash
git clone https://github.com/karvvan/maternity-care-policy-audit.git
cd maternity-care-policy-audit

git checkout -b mujin/작업이름          # 자기 브랜치를 만들고
# "무진님 업데이트" 폴더에 파일 추가/수정
git add "무진님 업데이트"
git commit -m "무슨 작업을 했는지 한 줄"
git push -u origin mujin/작업이름
```

푸시하면 GitHub에 **Compare & pull request** 버튼이 뜹니다. 눌러서 PR을 만들어 주시면
확인 후 `main`에 합칩니다.

## 부탁드리는 것

- `main` 브랜치에 직접 push하지 말아 주세요. 작업은 항상 자기 브랜치에서.
- 이 폴더 밖(`02_데이터`, `03_분석`, `04_제출물` 등)은 미리 얘기된 것만 수정해 주세요.
  같은 파일을 동시에 고치면 버전이 꼬입니다.
- 작업 시작 전에 `git pull` 한 번.
