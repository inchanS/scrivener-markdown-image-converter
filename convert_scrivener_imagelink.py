#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrivener 마크다운 파일 처리 도구
- 이미지 링크를 상대 경로로 변환
- 불필요한 단독 빈줄 정리
- 출력 파일명 지정 (기본: index.md)

사용법:
    python3 convert_scrivener_imagelink.py input.md [-o OUTPUT_FILE] [-i IMAGE_PATH]
"""
import re
import sys
import os
import shutil
import argparse
from typing import Dict

# --- 설정 변수 ---
# 이미지 경로 기본값을 여기서 쉽게 수정할 수 있습니다.
DEFAULT_IMAGE_PATH = ""

def read_markdown_file(file_path: str) -> str:
    """마크다운 파일을 읽어 내용을 반환합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except IOError as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        sys.exit(1)

def write_markdown_file(file_path: str, content: str) -> None:
    """마크다운 파일에 내용을 씁니다."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except IOError as e:
        print(f"파일을 쓰는 중 오류가 발생했습니다: {e}")
        sys.exit(1)

def create_output_file(input_path: str, output_path: str) -> None:
    """입력 파일을 지정된 출력 경로로 복사합니다."""
    try:
        shutil.copy2(input_path, output_path)
        print(f"작업 파일이 생성되었습니다: {output_path}")
    except IOError as e:
        print(f"작업 파일을 생성하는 중 오류가 발생했습니다: {e}")
        sys.exit(1)

def extract_references(content: str) -> Dict[str, str]:
    """마크다운 내용에서 참조 정의를 추출합니다."""
    ref_dict = {}
    ref_pattern = re.compile(r'^\[([^\]]+)\]:\s*(\S+)', re.MULTILINE)
    for match in ref_pattern.finditer(content):
        key = match.group(1)
        file_name = match.group(2)
        ref_dict[key] = file_name
    return ref_dict

def replace_image_links(content: str, ref_dict: Dict[str, str], image_path: str = DEFAULT_IMAGE_PATH) -> str:
    """이미지 링크를 새 형식으로 변환합니다. image_path가 제공되면 파일명 앞에 추가됩니다."""
    def replace_image(match):
        key = match.group(1)
        file_name = ref_dict.get(key, key + '.png')
        if image_path and not image_path.endswith('/'):
            path = image_path + '/'
        else:
            path = image_path
        return f'![]({path}{file_name})'

    return re.sub(r'!\[\]\[(.*?)\]', replace_image, content)

def remove_references(content: str) -> str:
    """참조 링크를 제거합니다 (각주 제외)."""
    return re.sub(r'^\[(?!\^)[^\]]+\]:\s.*(\n)?', '', content, flags=re.MULTILINE)

def clean_blank_lines(content: str) -> str:
    """불필요한 단독 빈줄을 정리합니다."""
    lines = content.splitlines(keepends=True)
    output = []
    n = len(lines)
    for i, line in enumerate(lines):
        core = line.rstrip('\n')
        if core.strip() == "":
            if core == "  ":
                output.append(line)
            elif core == "" or '\t' in core:
                prev_core = lines[i-1].rstrip('\n') if i > 0 else None
                next_core = lines[i+1].rstrip('\n') if i < n-1 else None
                prev_txt = prev_core is not None and prev_core.strip() != ""
                next_txt = next_core is not None and next_core.strip() != ""
                if prev_txt and next_txt:
                    continue
                output.append(line)
            else:
                output.append(line)
        else:
            output.append(line)
    return ''.join(output)

def replace_consecutive_blank_lines(content: str) -> str:
    """연속된 특정 빈줄 패턴을 &nbsp;로 바꿉니다."""
    lines = content.splitlines(keepends=True)
    result = []
    consecutive_count = 0
    i = 0
    while i < len(lines):
        if i + 1 < len(lines) and lines[i].rstrip('\n') == "  " and lines[i+1].strip() == "":
            consecutive_count += 1
            result.append(lines[i])
            if consecutive_count >= 2:
                newline = lines[i+1][len(lines[i+1].rstrip('\n')):]
                result.append("&nbsp;  " + newline)
            else:
                result.append(lines[i+1])
            i += 2
        else:
            consecutive_count = 0
            result.append(lines[i])
            i += 1
    return ''.join(result)

def convert_markdown(file_path: str, output_filename: str, image_path: str = DEFAULT_IMAGE_PATH) -> None:
    """지정된 이름으로 마크다운 파일을 생성하고 이미지 링크 변환 및 빈줄 정리를 수행합니다."""
    create_output_file(file_path, output_filename)
    content = read_markdown_file(output_filename)

    refs = extract_references(content)
    content = replace_image_links(content, refs, image_path)
    content = remove_references(content)
    content = clean_blank_lines(content)
    content = replace_consecutive_blank_lines(content)

    write_markdown_file(output_filename, content)
    print(f"파일 변환이 완료되었습니다: {output_filename}\n원본 파일은 변경되지 않았습니다: {file_path}")

def parse_arguments():
    """명령줄 인수를 파싱합니다."""
    parser = argparse.ArgumentParser(description='Scrivener 마크다운 파일 처리 도구')
    parser.add_argument('file_path', help='변환할 마크다운 파일 경로')
    parser.add_argument('-o', '--output', default='index.md', help='변환된 파일의 이름 (기본값: index.md)')
    # 기본값을 설정 변수에서 가져오도록 수정
    parser.add_argument(
        '-i',
        '--image-path',
        default=DEFAULT_IMAGE_PATH,
        help=f'이미지 상대 경로 (기본값: "{DEFAULT_IMAGE_PATH}" 입력 시 없음, 예: images)'
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    # 입력 파일이 위치한 디렉토리 경로를 가져옵니다.
    # 예: 'docs/chapter1.md' -> 'docs'
    input_directory = os.path.dirname(args.file_path)

    # 출력 경로를 '입력 파일 디렉토리'와 '출력 파일명'으로 조합합니다.
    # 예: 'docs' + 'index.md' -> 'docs/index.md'
    output_path = os.path.join(input_directory, args.output)

    # 새로 조합된 전체 출력 경로를 함수에 전달합니다.
    convert_markdown(args.file_path, output_path, args.image_path)