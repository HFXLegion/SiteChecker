import os
import qt.resources_rc
from threading import Thread
from modules.json import JSON
from modules.string import Format
from difflib import SequenceMatcher
from qt.main_window import Ui_MainWindow
from modules.site_parser import SiteParser
from modules.gui_base import Window, QtApplication, QPixmap, QPlainTextEdit


# Main window class (uses external QtDesigner window)
class MainWindow(Window):
    def __init__(self):
        super().__init__((480, 240), "Проверка надёжности сайтов")
        self.ui = Ui_MainWindow()  # creating instance of external QtDesigner window
        self.ui.setupUi(self)  # installing window
        # setting simple CSS
        self.setStyleSheet("*{background: #1e1e1e; color: white; font-size: 12px}"
                           "QPushButton{background: #0e639c; border-radius: 12px}")

        # Set clear action when user press clear button
        self.ui.clear_url.clicked.connect(lambda: self.ui.url_entry.clear())

    def __call__(self):
        super().__call__()


# Main script for checking websites content, rating and database
class SiteChecker:
    RATING_SITE = "https://www.mywot.com/scorecard/"  # Website for checking other sites rating

    def __init__(self, url, url_database_path: str):
        self.url_database_path = url_database_path
        self.__url, self.__site, self.__domain = Format.fit_url(url)

    # Method for checking site domain in database
    def database_check(self):
        with open(self.url_database_path, "r") as sites:  # Open database with read mode
            biggest_similatiry = 0  # Define integer var for biggest similarity with popular sites
            for site in sites.readlines():  # Iter sites database
                site = site.strip()  # Remove spaces and new lines in site domain
                # Set biggest similarity max value between site similarity ratio and biggest similarity
                biggest_similatiry = max(SequenceMatcher(None, site, self.__site).ratio(), biggest_similatiry)
                if site == self.__url or biggest_similatiry*100 == 100.0:  # If site full matches to current
                    return 0  # This site is in database

        return biggest_similatiry*100

    # Method for checking site content
    def content_check(self):
        # Combine text of all main web page tags
        main_text = ", ".join(SiteParser(self.__url).get_main_text().get_tags_text()).lower()
        triggers = JSON.read("trigger_words.dat")  # Load dict with trigger words
        total = set()  # Define set for trigger words
        for word, pattern in triggers.items():  # Iter dict with rigger words
            if word in main_text:  # If trigger word in web page main content
                total.add(pattern)  # Add trigger word to set
        return tuple(total)  # Return tuple of trigger words

    # Method for checking site rating
    def rating_check(self):
        url = self.RATING_SITE + self.__site  # Define URL with site rating
        try:  # Try to get rating value
            rating = float(SiteParser(url).get_tags("div", class_="StyledScorecardHeader__Detail-sc-1j5xgrs-12 gfahVA")[0].text)
        except IndexError:  # If site have no rating
            return -1
        else:
            return rating


# Main script
class Main:
    def __init__(self):
        self.app = QtApplication(on_exit_event=self.__on_exit)
        self.main_window = MainWindow()

        entry_geometry = self.main_window.ui.url_entry.geometry()
        self.main_window.ui.url_entry = QPlainTextEdit(self.main_window,
                                                       {"Key_Return": lambda: Thread(target=self.update_stats).start()})
        self.main_window.ui.url_entry.setGeometry(entry_geometry)

        self.main_window.ui.process_url.clicked.connect(lambda: Thread(target=self.update_stats).start())
        self.main_window()
        self.app()

    # Function for cleaning up all labels and icons
    def __clear_labels(self):
        self.main_window.ui.algorithm_check_label.clear()
        self.main_window.ui.algorithm_check_result.clear()
        self.main_window.ui.database_check_label.clear()
        self.main_window.ui.database_check_result.clear()
        self.main_window.ui.rating_check_label.clear()
        self.main_window.ui.rating_check_result.clear()

    # Function for changing database_check_label and database_check__icon
    def __update_algorithm_stats(self, text, icon_res):
        self.main_window.ui.algorithm_check_result.setPixmap(QPixmap(icon_res))
        self.main_window.ui.algorithm_check_label.setText(text)

    # Function for changing database_check_label and database_check__icon
    def __update_database_stats(self, text, icon_res):
        self.main_window.ui.database_check_result.setPixmap(QPixmap(icon_res))
        self.main_window.ui.database_check_label.setText(text)

    # Run checking site
    def update_stats(self):
        self.__clear_labels()  # Clear text on labels

        # Loading report
        self.main_window.ui.rating_check_label.setText("Проверка отзывов о сайте...")
        self.main_window.ui.algorithm_check_label.setText("Проверка содержания сайта...")
        self.main_window.ui.database_check_label.setText("Поиск сайта в базе данных...")

        # Creating instance of SiteChecker with using sites database ("checked_sites.dat")
        url_checker = SiteChecker(self.main_window.ui.url_entry.toPlainText(), "checked_sites.dat")

        try:  # Try to get response
            site_content_rating = url_checker.content_check()
        except SiteParser.SiteNotFoundError:  # If site not found
            self.__clear_labels()
            return self.__update_algorithm_stats("Ошибка при выполнении запроса", ":/main/warning.ico")
        except SiteParser.ConnectionAbortedError:  # If site aborted the connection
            self.__update_algorithm_stats("Ошибка соединения", ":/main/warning.ico")
        else:
            # Checking content and making deliverance
            if "casino" in site_content_rating:
                self.__update_algorithm_stats("Сайт определён как казино", ":/main/bad.ico")
            elif "scam" in site_content_rating:
                self.__update_algorithm_stats("Сайт определён как лохотрон", ":/main/bad.ico")
            elif "market" in site_content_rating:
                self.__update_algorithm_stats("Сайт определён как онлайн-магазин", ":/main/good.ico")
            elif "search" in site_content_rating:
                self.__update_algorithm_stats("Сайт определён как поисковая система", ":/main/good.ico")
            elif "conn_err" in site_content_rating:
                self.__update_algorithm_stats("Сайт не позволяет определить себя", ":/main/warning.ico")
            else:
                self.__update_algorithm_stats("Алгоритму не удалось определить тип сайта", ":/main/warning.ico")

        # Checking site in database
        url_similarity_score = url_checker.database_check()
        if not url_similarity_score:  # If site in database
            self.main_window.ui.database_check_result.setPixmap(QPixmap(":/main/good.ico"))
            self.main_window.ui.database_check_label.setText("Данный сайт является проверенным")
        elif url_similarity_score > 75:  # If site URL seems like a popular site
            self.main_window.ui.database_check_result.setPixmap(QPixmap(":/main/bad.ico"))
            self.main_window.ui.database_check_label.setText("Домен сайта похож на популярный, но не является им")
        else:  # If site not in database and URL is not the same as the popular site
            self.main_window.ui.database_check_result.setPixmap(QPixmap(":/main/good.ico"))
            self.main_window.ui.database_check_label.setText("Домен сайта не пытается быть похожим на популярный")

        # Checking site rating
        user_rating = url_checker.rating_check()
        if user_rating == -1:  # If site have no rating
            self.main_window.ui.rating_check_result.setPixmap(QPixmap(":/main/warning.ico"))
            self.main_window.ui.rating_check_label.setText("У данного сайта нет отзывов")
        elif user_rating < 3.5:  # If site have a bad rating
            self.main_window.ui.rating_check_result.setPixmap(QPixmap(":/main/bad.ico"))
            self.main_window.ui.rating_check_label.setText(f"Рейтинг сайта: {user_rating} из 5")
        else:  # If site have a good rating
            self.main_window.ui.rating_check_result.setPixmap(QPixmap(":/main/good.ico"))
            self.main_window.ui.rating_check_label.setText(f"Рейтинг сайта: {user_rating} из 5")

    # Method that calls when user closes main window
    def __on_exit(self):
        os.abort()


if __name__ == "__main__":
    Main()
