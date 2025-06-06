## Scrivener에서 컴파일한 마크다운 파일의 이미지 링크 변환 스크립트
![GitHub stars](https://img.shields.io/github/stars/inchans/scrivener-markdown-image-converter?style=flat&logo=apachespark)
![GitHub all releases](https://img.shields.io/github/downloads/inchanS/scrivener-markdown-image-converter/total?logo=github) ![GitHub release (latest by date)](https://img.shields.io/github/v/release/inchanS/scrivener-markdown-image-converter?logo=rocket)  ![GitHub](https://img.shields.io/github/license/inchanS/scrivener-markdown-image-converter)


Scrivener에서 작성한 글을 MultiMarkDown파일로 compile 했을 때, **이미지 링크를 표준 문법으로 변환**하는 스크립트.


### 배경
Scrivener에서 이미지와 함께 작성한 글을 Markdown 파일로 컴파일 하면 이미지 링크가 조금 이상하다. 

&nbsp;

```markdown
## 예제문
...(본문)

![][PastedGraphic3]

위 이미지와 같이...

...(생략)

[PastedGraphic3]: PastedGraphic3.png width=1287px height=947px

```

&nbsp;

위와 같이 일반적인 `![](image.jpg)` 형식의 문법이 아닌 **참조방식의 링크로 컴파일 되어있다.**  
이러한 마크다운 파일은 Marked2와 같은 뷰어에서는 정상적으로 이미지가 나타나지만, Obsidian 같은 앱에서는 제대로 나타나지 않는다.  
설사 Marked2를 사용한다 하더라도 추후 markdown파일을 수정할 때, 가독성이 현저히 떨어진다.
**때문에 이를 마크다운의 표준 이미지 링크로 변환하는 스크립트**를 고민하였다.  

&nbsp;

### 사용법
조건 : **python이 설치**되어 있어야 한다. 

&nbsp;

Scrivener에서 이미지가 첨부된 글을 마크다운 파일로 컴파일하면,  
새로운 폴더가 생성되어 그 안에 마크다운 파일과 이미지 파일이 함께 담겨있다.  

&nbsp;

그 md파일을 위 스크립트와 같은 경로(폴더)에 두고,  
터미널에서 다음과 같이 입력한 후 `enter`를 누른다.  

#### 기본 사용 (example.md -> example_converted.md 파일 생성 및 변환)
`python convert_scrivener_imagelink.py example.md`

#### 이미지 경로 지정
`python convert_scrivener_imagelink.py example.md -i /images/`

#### 변환된 파일의 접미사 지정
`python convert_scrivener_imagelink.py example.md -s _new`

&nbsp;

- `example.md` 부분에 변환하고자 하는 md파일명을 넣으면 된다.
- `-i` 또는 `--image-path` 옵션으로 이미지 경로를 지정할 수 있다. 기본값은 `/images/`
- `-s` 또는 `--suffix` 옵션으로 변환된 파일의 접미사를 지정할 수 있다. 기본값은 `_converted`


파인더에서 해당 경로의 터미널을 바로 여는 방법은 상위 폴더를 우클릭 한 후,`서비스 - 폴더에서 새로운 터미널 열기`를 누르면 된다.    

&nbsp;

#### 이미지 경로 설정 예시

이미지 경로는 마크다운에서 이미지를 참조할 때 사용되는 경로이며, 다음과 같은 형식으로 지정할 수 있다:

- 절대 경로: `-i /images/` → `![](/images/파일명.png)`
- 상대 경로: `-i ./images/` → `![](./images/파일명.png)`
- 경로 없음: `-i ""` → `![](파일명.png)`

사용할 마크다운 환경(Obsidian, Jekyll, Hugo 등)에 맞게 이미지 경로를 지정하면 된다.

&nbsp;  

### 개행처리 규칙 추가 update (v0.4)
#### 사용법 
1. 스크리브너에서 마크다운 변환 규칙 적용
- compile 화면에서 나타나는 MultiMarkdown format에서 `Edit Format...`을 클릭한다.
- 좌측 사이드메뉴에 있는 `Replacements`를 클릭한다.
- `+`을 눌러 규칙을 하나 생성한다.
  - `Replace(대체)`란에 입력할 수 있도록 준비한 후, `Option + Enter`를 함께 누른다. (참고로 눈에 나타나지 않는다. 신중히 한번만 누른다. 이는 줄바꿈을 의미한다.)
  - `With(포함)`란에 입력할 수 있도록 준비한 후, 아까와 마찬가지로 `Space key`를 두번 누른 후, `Option + Enter`키를 함께 누른다. (마크다운 문법에서의 줄바꿈인 공백 2칸과 줄바꿈 처리를 하는 것이다.)
  - 완성된 규칙을 체크하여 적용될 수 있도록 하고 포맷을 저장한다.
2. 마크다운 파일로 컴파일할 때, `Convert rich text to MultiMarkdown` 옵션에 체크하고 컴파일 한다.
3. 이전과 마찬가지로 스크립트를 실행한다. (위에 있는 '기본 사용'문단 참조)

마크다운 문법에서는 비어있는 여러 줄을 강제 개행하기가 불편하다.  
개행하기 위해서는 공백을 두칸 주고 줄바꿈을 하여야 하는데, 이 조차 두번 연속됐을 때에는 렌더러가 빈줄을 하나로만 인식하고 있다.  

하지만 스크리브너에서 문단간 또는 문단과 이미지 사이에 일부러 비어있는 여러 줄을 배치할 때가 있다.   
이에 스크리브너에서 여러줄의 빈줄을 마크다운 문법 및 렌더러에서도 비슷하게 여러 빈줄로 나타날 수 있도록 `&nbsp;  ` 문자로 대체하는 규칙을 추가하였다.  

### 주의
- 원본 파일 외에 변환된 새로운 파일이 생성된다.