#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrivener 마크다운 파일 처리 도구
- 이미지 링크 변환
- 불필요한 단독 빈줄 정리

사용법:
    python3 convert_scrivener_imagelink.py input.md [-i IMAGE_PATH] [-s SUFFIX]
"""
import re
import sys
import os
import shutil
import argparse
from typing import Dict

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

def create_copy(file_path: str, suffix: str = "_converted") -> str:
    """원본 파일의 복사본을 생성하고 새 파일 경로를 반환합니다."""
    file_name, file_ext = os.path.splitext(file_path)
    new_file_path = f"{file_name}{suffix}{file_ext}"
    
    try:
        shutil.copy2(file_path, new_file_path)
        print(f"복사본이 생성되었습니다: {new_file_path}")
        return new_file_path
    except IOError as e:
        print(f"복사본을 생성하는 중 오류가 발생했습니다: {e}")
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

def replace_image_links(content: str, ref_dict: Dict[str, str], image_path: str = "/images/") -> str:
    """이미지 링크를 새 형식으로 변환합니다."""
    def replace_image(match):
        key = match.group(1)
        file_name = ref_dict.get(key, key + '.png')  # 기본값: 키값에 .png 추가
        return f'![]({image_path}{file_name})'

    return re.sub(r'!\[\]\[(.*?)\]', replace_image, content)

def remove_references(content: str) -> str:
    """참조 링크를 제거합니다 (각주 제외)."""
    return re.sub(r'^\[(?!\^)[^\]]+\]:\s.*(\n)?', '', content, flags=re.MULTILINE)

def clean_blank_lines(content: str) -> str:
    """
    - 공백 2칸만 있는 줄: 유지
    - 완전 빈줄인 줄이, 앞뒤 모두 텍스트 줄인 단독 빈줄: 제거
    - 그 외 줄: 그대로 유지
    """
    lines = content.splitlines(keepends=True)
    output = []
    n = len(lines)
    for i, line in enumerate(lines):
        core = line.rstrip('\n')
        # 공백만 있는 줄 처리
        if core.strip() == "":
            if core == "  ":
                # Scrivener 실제 빈줄
                output.append(line)
            elif core == "":
                # 완전 빈줄
                prev_core = lines[i-1].rstrip('\n') if i > 0 else None
                next_core = lines[i+1].rstrip('\n') if i < n-1 else None
                prev_txt = prev_core is not None and prev_core.strip() != ""
                next_txt = next_core is not None and next_core.strip() != ""
                # 앞뒤 모두 텍스트면 제거
                if prev_txt and next_txt:
                    continue
                output.append(line)
            else:
                # 탭 1개, 공백 3칸 등 기타 공백 줄
                output.append(line)
        else:
            # 내용 있는 줄
            output.append(line)
    return ''.join(output)

def convert_markdown(file_path: str, image_path: str = "/images/", suffix: str = "_converted") -> None:
    """마크다운 파일을 복사본을 생성하고 이미지 링크 변환 및 빈줄 정리 수행"""
    new_path = create_copy(file_path, suffix)
    content = read_markdown_file(new_path)

    # 1) 참조 정의 추출 → 2) 이미지 링크 변환 → 3) 참조 제거
    refs = extract_references(content)
    content = replace_image_links(content, refs, image_path)
    content = remove_references(content)
    # 4) 불필요 빈줄 정리
    content = clean_blank_lines(content)

    write_markdown_file(new_path, content)
    print(f"파일 변환이 완료되었습니다: {new_path}\n원본 파일은 변경되지 않았습니다: {file_path}")

def parse_arguments():
    """명령줄 인수를 파싱합니다."""
    parser = argparse.ArgumentParser(description='Scrivener 마크다운 이미지 링크 변환 도구')
    parser.add_argument('file_path', help='변환할 마크다운 파일 경로')
    parser.add_argument('-i', '--image-path', default='/images/', help='이미지 경로 (기본값: /images/)')
    parser.add_argument('-s', '--suffix', default='_converted', help='변환된 파일의 접미사 (기본값: _converted)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    convert_markdown(args.file_path, args.image_path, args.suffix)