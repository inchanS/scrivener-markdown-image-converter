## Scrivener에서 컴파일한 마크다운 파일의 이미지 링크 변환 스크립트

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

그 md파일을 위 스크립트가 같은 경로(폴더)에 두고,  
터미널에서 다음과 같이 입력한 후 `enter`를 누른다.  

#### 기본 사용 (example.md -> example_converted.md 파일 생성 및 변환)
`python convert_scrivener_imagelink.py example.md`

#### 이미지 경로 지정
`python convert_scrivener_imagelink.py example.md -i /images/`

#### 변환된 파일의 접미사 지정
`python convert_scrivener_imagelink.py example.md -s _new`

&nbsp;

- compiled_file.md 부분에 변환하고자 하는 md파일명을 넣으면 된다.
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

### 주의
- 원본 파일 외에 변환된 새로운 파일이 생성된다.