#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrivener 마크다운 파일 처리 도구
- 이미지 링크를 상대 경로로 변환
- 빈줄 정리 옵션(-c): 불필요한 단독 빈줄 정리 및 연속 빈줄의 <br> 변환 ( <br> 주변 제외 )
- 출력 파일명 지정 (기본: 입력 파일명에 _converted 접미사를 붙인 이름)

사용법:
    python3 convert_scrivener_imagelink.py input.md [-o OUTPUT_FILE] [-i IMAGE_PATH] [-c]
"""
import re
import sys
import os
import shutil
import argparse
from typing import Dict, Set

# --- 설정 변수 ---
# 이미지 경로 기본값을 여기서 쉽게 수정할 수 있습니다.
DEFAULT_IMAGE_PATH = "/images/"

def read_markdown_file(file_path: str) -> str:
    """마크다운 파일을 읽어 내용을 반환합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except IOError as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}", file=sys.stderr)
        sys.exit(1)

def write_markdown_file(file_path: str, content: str) -> None:
    """마크다운 파일에 내용을 씁니다."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except IOError as e:
        print(f"파일을 쓰는 중 오류가 발생했습니다: {e}", file=sys.stderr)
        sys.exit(1)

def create_output_file(input_path: str, output_path: str) -> None:
    """입력 파일을 지정된 출력 경로로 복사합니다."""
    try:
        shutil.copy2(input_path, output_path)
        print(f"작업 파일이 생성되었습니다: {output_path}")
    except IOError as e:
        print(f"작업 파일을 생성하는 중 오류가 발생했습니다: {e}", file=sys.stderr)
        sys.exit(1)

def extract_references(content: str) -> Dict[str, str]:
    """마크다운 내용에서 참조 정의를 추출합니다 (각주 제외)."""
    ref_dict = {}
    ref_pattern = re.compile(r'^\[(?!\^)([^\]]+)\]:\s*(\S+)', re.MULTILINE)
    for match in ref_pattern.finditer(content):
        key = match.group(1)
        file_name = match.group(2)
        ref_dict[key] = file_name
    return ref_dict

def find_image_reference_keys(content: str) -> Set[str]:
    """본문에서 이미지 참조(![][key])로 사용된 키 목록을 반환합니다."""
    return set(re.findall(r'!\[\]\[(.*?)\]', content))

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

def remove_references(content: str, used_keys: Set[str]) -> str:
    """이미지 변환에 사용된 참조 정의만 제거합니다 (일반 하이퍼링크 참조와 각주는 유지)."""
    for key in used_keys:
        pattern = r'^\[' + re.escape(key) + r'\]:\s.*(\n)?'
        content = re.sub(pattern, '', content, flags=re.MULTILINE)
    return content

def clean_blank_lines(content: str) -> str:
    """불필요한 단독 빈줄을 정리하되, <br> 태그 주변은 유지합니다."""
    lines = content.splitlines(keepends=True)
    output = []
    n = len(lines)
    for i, line in enumerate(lines):
        core = line.rstrip('\n')
        if core.strip() == "":
            prev_line = lines[i-1] if i > 0 else ""
            next_line = lines[i+1] if i < n-1 else ""

            # <br> 태그 인접 여부 확인
            if "<br>" in prev_line or "<br>" in next_line:
                output.append(line)
                continue

            if core == "  ":
                output.append(line)
            elif core == "" or '\t' in core:
                prev_core = prev_line.rstrip('\n')
                next_core = next_line.rstrip('\n')
                prev_txt = prev_core.strip() != ""
                next_txt = next_core.strip() != ""
                if prev_txt and next_txt:
                    continue
                output.append(line)
            else:
                output.append(line)
        else:
            output.append(line)
    return ''.join(output)

def replace_consecutive_blank_lines(content: str) -> str:
    """연속된 특정 빈줄 패턴을 <br>로 바꿉니다."""
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
                result.append(newline)
                result.append("<br>  " + newline)
                result.append(newline)
            else:
                result.append(lines[i+1])
            i += 2
        else:
            consecutive_count = 0
            result.append(lines[i])
            i += 1
    return ''.join(result)

def convert_markdown(file_path: str, output_filename: str, image_path: str = DEFAULT_IMAGE_PATH, clean_lines: bool = False) -> None:
    """지정된 이름으로 마크다운 파일을 생성하고 이미지 링크 변환(및 옵션 시 빈줄 정리)을 수행합니다."""
    create_output_file(file_path, output_filename)
    content = read_markdown_file(output_filename)

    refs = extract_references(content)
    used_keys = find_image_reference_keys(content)
    content = replace_image_links(content, refs, image_path)
    content = remove_references(content, used_keys)

    if clean_lines:
        # 순서: 연속 빈줄을 <br>로 먼저 바꾼 뒤, 일반 빈줄 정리 실행 (보존 로직 작동을 위함)
        content = replace_consecutive_blank_lines(content)
        content = clean_blank_lines(content)

    write_markdown_file(output_filename, content)
    print(f"파일 변환이 완료되었습니다: {output_filename}\n원본 파일은 변경되지 않았습니다: {file_path}")

def parse_arguments():
    """명령줄 인수를 파싱합니다."""
    parser = argparse.ArgumentParser(description='Scrivener 마크다운 파일 처리 도구')
    parser.add_argument('file_path', help='변환할 마크다운 파일 경로')
    parser.add_argument('-o', '--output', default=None, help='변환된 파일의 이름 (기본값: 입력 파일명에 _converted 접미사를 붙인 이름, 예: example.md -> example_converted.md)')
    # 기본값을 설정 변수에서 가져오도록 수정
    parser.add_argument(
        '-i',
        '--image-path',
        default=DEFAULT_IMAGE_PATH,
        help=f'이미지 경로 (기본값: {DEFAULT_IMAGE_PATH}, 경로 없이 파일명만 쓰려면 -i "" 지정)'
    )
    parser.add_argument(
        '-c',
        '--clean-lines',
        action='store_true',
        help='빈줄 정리 및 연속 빈줄의 <br> 변환 활성화 (v0.4 개행처리 규칙을 적용해 컴파일한 파일 전용)'
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    # 입력 파일이 위치한 디렉토리 경로를 가져옵니다.
    # 예: 'docs/chapter1.md' -> 'docs'
    input_directory = os.path.dirname(args.file_path)

    # 출력 파일명이 지정되지 않으면 입력 파일명에 _converted 접미사를 붙입니다.
    # 예: 'example.md' -> 'example_converted.md'
    if args.output is None:
        base, ext = os.path.splitext(os.path.basename(args.file_path))
        output_filename = f"{base}_converted{ext}"
    else:
        output_filename = args.output

    # 출력 경로를 '입력 파일 디렉토리'와 '출력 파일명'으로 조합합니다.
    # 예: 'docs' + 'example_converted.md' -> 'docs/example_converted.md'
    output_path = os.path.join(input_directory, output_filename)

    if os.path.abspath(output_path) == os.path.abspath(args.file_path):
        print("출력 파일이 입력 파일과 같습니다. 다른 이름을 지정해주세요.", file=sys.stderr)
        sys.exit(1)

    if os.path.exists(output_path):
        answer = input(f"'{output_path}' 파일이 이미 존재합니다. 덮어쓸까요? [y/N]: ")
        if answer.strip().lower() != 'y':
            print("작업을 취소했습니다.")
            sys.exit(0)

    # 새로 조합된 전체 출력 경로를 함수에 전달합니다.
    convert_markdown(args.file_path, output_path, args.image_path, args.clean_lines)
