import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier


class AI:
    class Container:
        def __init__(self, vectorizer, classifizer):
            self.vectorizer = vectorizer
            self.classifizer = classifizer

        def get(self):
            return self.vectorizer, self.classifizer

    class TokensRequiredError(Exception):
        def __init__(self):
            super().__init__("Tokens required")

    def __init__(self,
                 vectorizer=TfidfVectorizer(analyzer="char_wb"),
                 classifizer=RandomForestClassifier(n_estimators=5000)):
        self.vectorizer = vectorizer
        self.classifizer = classifizer

        self.learn_database = dict()
        self.__is_learned = False

    def add_single(self, request, response):
        self.learn_database[request] = response

    def save_to_file(self, path: str):
        with open(path, "wb") as asset:
            pickle.dump(self.Container(self.vectorizer, self.classifizer), asset)

    def load_from_file(self, path: str):
        with open(path, "rb") as asset:
            self.vectorizer, self.classifizer = pickle.load(asset).get()
        self.__is_learned = True

    def learn(self):
        self.classifizer.fit(self.vectorizer.fit_transform(list(self.learn_database.keys())), list(self.learn_database.values()))
        self.__is_learned = True

    def response(self, text):
        if not self.__is_learned:
            self.learn()
        return self.classifizer.predict(self.vectorizer.transform([text]))[0]