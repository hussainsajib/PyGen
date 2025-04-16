import json


class Reciter:
    tag: str = None
    eng_name: str = None
    bangla_name: str = None
    folder_name: str = None
    database_name: str = None

    def __init__(self, tag) -> None:
        self.tag = tag
        with open("data/reciter_info.json", "r", encoding="utf-8") as f:
            reciters = json.load(f)
            for key, value in reciters.items():
                if key == self.tag:
                    self.eng_name = value["english_name"]
                    self.bangla_name = value["bangla_name"]
                    self.folder_name = value.get("folder", None)
                    self.database_name = value.get("database", None)