import re
import sys

def convert_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 참조 정의 추출: 예를 들어, [sample1]: sample1.png width=800px height=400px
    ref_dict = {}
    ref_pattern = re.compile(r'^\[([^\]]+)\]:\s*(\S+)', re.MULTILINE)
    for match in ref_pattern.finditer(content):
        key = match.group(1)
        file_name = match.group(2)
        ref_dict[key] = file_name

    # 이미지 링크 변환: 참조 정의에서 실제 파일명을 찾아 반영
    def replace_image(match):
        key = match.group(1)
        file_name = ref_dict.get(key, key + '.png')  # 기본값: 키값에 .png 추가
        return f'![]({file_name})'

    content = re.sub(r'!\[\]\[(.*?)\]', replace_image, content)

    # 참조 링크 제거 (빈 줄 포함), 주석은 제외
    content = re.sub(r'^\[(?!\^)[^\]]+\]:\s.*(\n)?', '', content, flags=re.MULTILINE)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python script.py [파일경로]")
        sys.exit(1)
    convert_markdown(sys.argv[1])
