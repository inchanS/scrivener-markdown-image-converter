#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""convert_scrivener_imagelink.py 단위 테스트

실행: python3 -m unittest test_convert_scrivener_imagelink.py
"""
import unittest

from convert_scrivener_imagelink import (
    extract_references,
    find_image_reference_keys,
    replace_image_links,
    remove_references,
    clean_blank_lines,
    replace_consecutive_blank_lines,
)


class TestExtractReferences(unittest.TestCase):
    def test_extracts_image_reference(self):
        content = "[PastedGraphic3]: PastedGraphic3.png width=1287px height=947px\n"
        self.assertEqual(extract_references(content), {"PastedGraphic3": "PastedGraphic3.png"})

    def test_excludes_footnotes(self):
        content = "[^1]: 각주 내용입니다.\n[img]: img.png\n"
        self.assertEqual(extract_references(content), {"img": "img.png"})


class TestReplaceImageLinks(unittest.TestCase):
    def test_replaces_with_image_path(self):
        content = "![][img]"
        result = replace_image_links(content, {"img": "img.png"}, "images")
        self.assertEqual(result, "![](images/img.png)")

    def test_image_path_trailing_slash(self):
        result = replace_image_links("![][img]", {"img": "img.png"}, "images/")
        self.assertEqual(result, "![](images/img.png)")

    def test_no_image_path(self):
        result = replace_image_links("![][img]", {"img": "img.png"}, "")
        self.assertEqual(result, "![](img.png)")

    def test_missing_reference_falls_back_to_png(self):
        result = replace_image_links("![][photo]", {}, "")
        self.assertEqual(result, "![](photo.png)")


class TestRemoveReferences(unittest.TestCase):
    def test_removes_only_used_image_references(self):
        content = (
            "본문 [여기][mylink] 참조.\n"
            "[img]: img.png width=100px\n"
            "[mylink]: https://example.com\n"
            "[^1]: 각주 내용입니다.\n"
        )
        used_keys = {"img"}
        result = remove_references(content, used_keys)
        self.assertNotIn("[img]:", result)
        self.assertIn("[mylink]: https://example.com", result)
        self.assertIn("[^1]: 각주 내용입니다.", result)


class TestFindImageReferenceKeys(unittest.TestCase):
    def test_finds_used_keys(self):
        content = "![][a]\n텍스트\n![][b]\n[c]: c.png\n"
        self.assertEqual(find_image_reference_keys(content), {"a", "b"})


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


class TestEndToEnd(unittest.TestCase):
    def test_full_pipeline_without_clean_lines(self):
        content = (
            "# 제목\n\n"
            "본문 첫 줄.\n\n"
            "![][PastedGraphic3]\n\n"
            "링크는 [여기][mylink] 참조.\n\n"
            "[PastedGraphic3]: PastedGraphic3.png width=1287px height=947px\n"
            "[mylink]: https://example.com\n"
        )
        refs = extract_references(content)
        used_keys = find_image_reference_keys(content)
        content = replace_image_links(content, refs, "images")
        content = remove_references(content, used_keys)

        self.assertIn("![](images/PastedGraphic3.png)", content)
        self.assertNotIn("[PastedGraphic3]:", content)
        self.assertIn("[mylink]: https://example.com", content)
        # 빈줄 정리 옵션을 켜지 않으면 문단 구분 빈줄이 유지된다.
        self.assertIn("본문 첫 줄.\n\n", content)


if __name__ == "__main__":
    unittest.main()
