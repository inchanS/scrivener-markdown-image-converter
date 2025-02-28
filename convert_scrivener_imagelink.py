import re
import sys

def convert_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 이미지 링크 변환
    content = re.sub(r'!\[\]\[(.*?)\]', r'![](\1.png)', content)

    # 참조 링크 제거 (빈 줄 포함)
    content = re.sub(r'^\[[^\]]+\]:\s.*(\n)?', '', content, flags=re.MULTILINE)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python script.py [파일경로]")
        sys.exit(1)
    convert_markdown(sys.argv[1])

