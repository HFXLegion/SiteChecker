import json
from modules.ai_api import AI

if __name__ == "__main__":
    ai = AI()
    sites_file = open("trigger_words.json", "r")
    sites = json.load(sites_file).items()
    sites_file.close()
    for keyword, rating in sites:
        ai.add_single(keyword.lower(), str(rating))

    ai.learn()
    ai.save_to_file("ai.db")