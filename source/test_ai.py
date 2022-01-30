from modules.ai_api import AI
from modules.site_parser import SiteParser

if __name__ == "__main__":
    ai = AI()

    ai.load_from_file("ai.db")

    parser = SiteParser("https://yandex.ru")
    for tag in parser.get_main_text().get_tags_text():
        print(tag, ai.response(tag.lower()))