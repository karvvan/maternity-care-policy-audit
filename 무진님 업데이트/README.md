# 무진님 업데이트

무진님 작업물을 올리는 폴더입니다. 이 폴더 안은 편하게 쓰셔도 됩니다.

## 웹으로 올리기 (제일 간단합니다)

아래 주소로 들어가 파일을 끌어다 놓으시면 됩니다.

https://github.com/karvvan/maternity-care-policy-audit/upload/main/%EB%AC%B4%EC%A7%84%EB%8B%98%20%EC%97%85%EB%8D%B0%EC%9D%B4%ED%8A%B8

올린 뒤 아래쪽에서 **"Create a new branch for this commit and start a pull request"** 를
선택하고 **Propose changes** 를 눌러주세요.

## 터미널로 올리기

처음 한 번만:

```bash
git clone https://github.com/karvvan/maternity-care-policy-audit.git
cd maternity-care-policy-audit
git config core.hooksPath .githooks     # 저장소 공통 설정
```

작업할 때마다:

```bash
git pull
git checkout -b mujin/작업이름
# "무진님 업데이트" 폴더에 파일 추가/수정
git add "무진님 업데이트"
git commit -m "무슨 작업을 했는지 한 줄"
git push -u origin mujin/작업이름
```

push하면 GitHub에 **Compare & pull request** 버튼이 뜹니다. 눌러서 PR을 올려주시면
확인 후 합치겠습니다.

## 참고

작업은 이 폴더 안에서 부탁드립니다. 다른 폴더도 자유롭게 보셔도 되지만,
고쳐야 할 부분이 보이면 직접 수정하시기보다 알려주시면 반영하겠습니다.
