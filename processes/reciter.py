import json


class Reciter:
    tag: str = None
    eng_name: str = None
    bangla_name: str = None
    folder_name: str = None

    def __init__(self, tag) -> None:
        self.tag = tag
        with open("data/reciter_info.json", "r", encoding="utf-8") as f:
            reciters = json.load(f)
            for k, v in reciters.items():
                if k == self.tag:
                    self.eng_name = v["english_name"]
                    self.bangla_name = v["bangla_name"]
                    self.folder_name = v.get("folder", None)