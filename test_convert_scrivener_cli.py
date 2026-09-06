#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""실제 파일과 명령줄을 이용한 통합 테스트. 실행: python3 -m unittest discover -v"""
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from convert_scrivener_imagelink import convert_markdown


SCRIPT = Path(__file__).with_name('convert_scrivener_imagelink.py')

# 이미지 참조, 일반 링크, 각주, 단독 빈줄, 연속 빈줄을 함께 검증합니다.
SOURCE = (
    "# 제목\n\n본문  \n  \n\n  \n\n"
    "![][img]\n[링크][site]\n각주[^1]\n"
    "[img]: photo.png width=100px height=50px\n"
    "[site]: https://example.com\n[^1]: 설명\n"
)
CLEANED = (
    "# 제목\n본문  \n  \n\n  \n\n<br>  \n\n"
    "![][img]\n[링크][site]\n각주[^1]\n"
    "[img]: photo.png width=100px height=50px\n"
    "[site]: https://example.com\n[^1]: 설명\n"
)


class TestCommandLine(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / '한글 문서.md'
        self.source.write_text(SOURCE, encoding='utf-8')
        self.output = self.source.with_name('한글 문서_converted.md')

    def run_cli(self, *args, answer=''):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.source), *args],
            input=answer, text=True, encoding='utf-8', capture_output=True,
            timeout=10,
        )
        # 성공·취소·오류 여부와 무관하게 원본 파일을 보존해야 합니다.
        self.assertEqual(self.source.read_text(encoding='utf-8'), SOURCE)
        return result

    def test_three_modes(self):
        for args, expected in [
            ([], SOURCE.replace('![][img]', '![](/images/photo.png)').replace(
                '[img]: photo.png width=100px height=50px\n', '')),
            (['-c'], CLEANED.replace('![][img]', '![](/images/photo.png)').replace(
                '[img]: photo.png width=100px height=50px\n', '')),
            (['--only-clean-lines'], CLEANED),
        ]:
            with self.subTest(args=args):
                result = self.run_cli(*args, answer='y\n')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(self.output.read_text(encoding='utf-8'), expected)

    def test_long_clean_option_and_custom_paths(self):
        result = self.run_cli('--clean-lines', '-i', 'assets', '-o', 'result.md')
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = CLEANED.replace('![][img]', '![](assets/photo.png)').replace(
            '[img]: photo.png width=100px height=50px\n', '')
        self.assertEqual(self.source.with_name('result.md').read_text(encoding='utf-8'), expected)

    def test_image_path_is_ignored_in_clean_only_mode(self):
        result = self.run_cli('--only-clean-lines', '-i', 'unused')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.output.read_text(encoding='utf-8'), CLEANED)

    def test_conflicting_modes_fail_before_creating_output(self):
        result = self.run_cli('-c', '--only-clean-lines')
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.output.exists())

    def test_same_input_and_output_is_rejected(self):
        result = self.run_cli('--only-clean-lines', '-o', self.source.name)
        self.assertEqual(result.returncode, 1)
        self.assertIn('출력 파일이 입력 파일과 같습니다', result.stderr)

    def test_existing_output_requires_confirmation(self):
        self.output.write_text('기존 내용', encoding='utf-8')
        result = self.run_cli('--only-clean-lines', answer='n\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.output.read_text(encoding='utf-8'), '기존 내용')
        result = self.run_cli('--only-clean-lines', answer='y\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.output.read_text(encoding='utf-8'), CLEANED)

    def test_existing_positional_api_and_new_keyword(self):
        # 기존 네 개 위치 인수 호출과 새 키워드 호출을 모두 지원합니다.
        with contextlib.redirect_stdout(io.StringIO()):
            convert_markdown(str(self.source), str(self.output), '', True)
        expected = CLEANED.replace('![][img]', '![](photo.png)').replace(
            '[img]: photo.png width=100px height=50px\n', '')
        self.assertEqual(self.output.read_text(encoding='utf-8'), expected)
        with contextlib.redirect_stdout(io.StringIO()):
            convert_markdown(str(self.source), str(self.output), only_clean_lines=True)
        self.assertEqual(self.output.read_text(encoding='utf-8'), CLEANED)
        self.assertEqual(self.source.read_text(encoding='utf-8'), SOURCE)


if __name__ == '__main__':
    unittest.main()
