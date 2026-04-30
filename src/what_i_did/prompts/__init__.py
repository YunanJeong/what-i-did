from what_i_did.prompts import en, ko


def get(lang: str):
    if lang == "en":
        return en
    return ko
