import json
class JSON:
    @staticmethod
    def read(file: str):
        with open(file, "r", encoding="utf-8") as file_read:
            return json.load(file_read)

    @staticmethod
    def write(data: dict, file: str):
        with open(file, "w", encoding="utf-8") as file_write:
            return json.dump(data, file_write, ensure_ascii=False, indent=2, separators=(",", ": "))