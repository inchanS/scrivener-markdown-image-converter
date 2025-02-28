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

`python convert_scrivener_imagelink.py compiled_file.md`  

&nbsp;

- compiled_file.md 부분에 변환하고자 하는 md파일명을 넣으면 된다.

파인더에서 해당 경로의 터미널을 바로 여는 방법은 상위 폴더를 우클릭 한 후,`서비스 - 폴더에서 새로운 터미널 열기`를 누르면 된다.    

&nbsp;

#### 이미지파일의 경로 수정
convert_scrivener_imagelink.py의 20번째 줄을 수정하여 `경로`를 다음과 같이 조정할 수 있다.  

`return f'![](/images/{file_name})'`  

&nbsp;

위 코드에서 `/images/`부분을 본인이 사용하는 이미지 폴더경로(상대경로)로 바꾸어주면 된다.  
만약 마크다운 파일과 같은 폴더에 이미지를 저장하고 사용한다면 `return f'![]({file_name})'` 이렇게 경로를 완전히 빼면 된다.

&nbsp;

### 주의
- 이미지 링크를 변환하고자 하는 md파일의 복사본으로 변환할 것!
- 또는 반드시 원본 파일은 백업 후 변환할 것!