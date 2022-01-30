import unittest
from modules.site_parser import SiteParser


class SiteParserTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.site_parser = SiteParser("yandex.ru")

    def test_raising_SiteNotFoundError(self):
        self.assertRaises(SiteParser.SiteNotFoundError, self.site_parser.change_url("foo"))

    def test_get_all_text(self):
        self.assertEqual(type(self.site_parser.get_all_text()), SiteParser.TagContainer)

    def test_get_main_text(self):
        self.assertEqual(type(self.site_parser.get_main_text()), SiteParser.TagContainer)

    def test_get_headers(self):
        self.assertEqual(type(self.site_parser.get_headers()), SiteParser.TagContainer)


if __name__ == "__main__":
    unittest.main()