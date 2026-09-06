#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""개행 규칙 단위 테스트. 실행: python3 -m unittest test_convert_scrivener_linebreaks"""
import unittest

from convert_scrivener_imagelink import clean_blank_lines, replace_consecutive_blank_lines


class TestCleanBlankLines(unittest.TestCase):
    def test_removes_plain_blank_line_between_text(self):
        content = "문단1\n\n문단2\n"
        self.assertEqual(clean_blank_lines(content), "문단1\n문단2\n")

    def test_keeps_two_space_blank_line(self):
        content = "문단1  \n  \n문단2  \n"
        self.assertEqual(clean_blank_lines(content), content)

    def test_keeps_blank_lines_around_br(self):
        content = "문단1  \n\n<br>  \n\n문단2  \n"
        self.assertEqual(clean_blank_lines(content), content)


class TestReplaceConsecutiveBlankLines(unittest.TestCase):
    def test_single_pair_untouched(self):
        content = "문단1  \n  \n\n문단2\n"
        self.assertNotIn("<br>", replace_consecutive_blank_lines(content))

    def test_second_consecutive_pair_becomes_br(self):
        content = "문단1  \n  \n\n  \n\n문단2\n"
        result = replace_consecutive_blank_lines(content)
        self.assertIn("<br>  \n", result)


if __name__ == "__main__":
    unittest.main()
