from dataclasses import dataclass


@dataclass
class Translator:
    _lang = 'ru'
    texts: dict[str, dict]

    def _set_lang(self, lang: str):
        self._lang = lang

    def __getitem__(self, item: str) -> str:
        try:
            return self.texts[self._lang][item]
        except IndexError as err:
            raise IndexError(f'{err}: there is no key "{item}"')


def create_translator(locale: str) -> Translator:
    from utils.translator.Lexicon import get_languages
    texts = {}
    for lang in get_languages():
        if list(lang.keys())[0] == locale:
            texts.update(lang)
            break
    return Translator(texts)


def recreate_locales(model_dict: dict, old_locale: str, new_locale: str) -> dict:
    from utils.translator.Lexicon import get_languages
    for lang in get_languages():
        if list(lang.keys())[0] == old_locale:
            old_locale = lang
        if list(lang.keys())[0] == new_locale:
            new_locale = lang
    new_model_dict = {}
    for key, value in model_dict.items():
        for k, v in old_locale.get(list(old_locale.keys())[0]).items():
            if value == v:
                new_model_dict[key] = k
    for key, value in new_model_dict.items():
        for k, v in new_locale.get(list(new_locale.keys())[0]).items():
            if value == k:
                new_model_dict[key] = v
    return new_model_dict