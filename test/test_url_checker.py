import unittest
from .__service__ import get_sources_path
from source.main import CheckURL

SOURCES = get_sources_path()


class UrlCheckerTestCase(unittest.TestCase):
    def setUp(self):
        self.url_checker = CheckURL("yandex.ru", f"{SOURCES}\\checked_sites.dat")

    def test_url_rating(self):
        self.assertGreater(self.url_checker.rating_check(), 3.5)

    def test_database_check(self):
        self.assertEqual(self.url_checker.database_check(), 0)


if __name__ == "__main__":
    unittest.main()

