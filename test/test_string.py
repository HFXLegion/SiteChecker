import unittest
from modules.string import Format


class FormatTestCase(unittest.TestCase):
    def test_slash_to_back_slash(self):
        self.assertEqual(Format.slash_to_back_slash("C:\\Windows\\System32"), "C:/Windows/System32")

    def test_back_slash_to_double_slash(self):
        self.assertEqual(Format.back_slash_to_double_slash("C:/Windows/System32"), "C:\\Windows\\System32")

    def test_remove_brackets(self):
        self.assertEqual(Format.remove_brackets("{a: 'any', b: [1, 2, 3]}"), "a: 'any', b: 1, 2, 3")

    def test_url_fit(self):
        fit = Format.fit_url
        self.assertEqual(fit("google.com")[2], "https://google.com")
        self.assertEqual(fit("www.google.com")[2], "https://google.com")
        self.assertEqual(fit("www.google.com/search=None")[2], "https://google.com")


if __name__ == "__main__":
    unittest.main()
