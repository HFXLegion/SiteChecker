import requests
from modules.string import Format
from bs4 import BeautifulSoup


class SiteParser:
    class SiteNotFoundError(BaseException):
        def __init__(self, url):
            super().__init__(f"Site {url} not exists")

    class ConnectionAbortedError(BaseException):
        def __init__(self, url):
            super().__init__(f"Site {url} has aborted connection")

    class TagContainer:
        def __init__(self, tags: list = None):
            self.__tags = tags if tags is not None else list()

        def add_tag(self, tag):
            self.__tags.append(tag)

        def get_tags_text(self):
            for tag in self.__tags:
                yield tag.text

        def __getitem__(self, item: int):
            return self.__tags[item]

    def __init__(self, url, params: dict = None):
        if params is None:
            params = dict()
        self.parser = self.__get_parser(Format.fit_url(url)[0], params)

    def __get_parser(self, url, params):
        try:
            response = requests.get(url, params)
        except requests.exceptions.ConnectionError as conn_err:
            if 'Connection aborted.' in str(conn_err.args[0]):
                raise self.ConnectionAbortedError(url)
            else:
                raise self.SiteNotFoundError(url)
        if 'charset' in response.headers.get('content-type', '').lower():
            encoding = response.encoding
        else:
            encoding = None
        return BeautifulSoup(response.content, "html.parser", from_encoding=encoding)

    def change_url(self, new_url, params: dict = None) -> None:
        if params is None:
            params = dict()
        self.parser = self.__get_parser(Format.fit_url(new_url)[2], params)

    def get_tags(self, tag="strong", class_="main") -> TagContainer:
        return self.TagContainer(self.parser.find_all(tag, class_=class_))

    def get_headers(self) -> TagContainer:
        return self.TagContainer(self.parser.find_all(("h1", "h2", "h3", "h4", "h5", "h6")))

    def get_main_text(self) -> TagContainer:
        return self.TagContainer(self.parser.find_all(("title", "strong", "p", "h1", "h2", "h3", "h4", "h5", "h6")))

    def get_all_text(self) -> TagContainer:
        return self.TagContainer(self.parser.find_all(("a", "title", "p", "ul", "li", "div", "span", "strong"
                                                       , "h1", "h2", "h3", "h4", "h5", "h6")))
