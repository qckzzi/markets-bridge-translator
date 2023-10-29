from time import (
    sleep,
)

import requests
from googletrans import (
    Translator,
)

import config


translator = Translator()


def translate_categories():
    url = config.untranslated_category_url

    while True:
        untranslated_category = requests.get(url).json()

        if not untranslated_category.get('id'):
            break

        category_pk = untranslated_category.get('id')
        translated_category = translate_category(untranslated_category)
        send_category(category_pk, translated_category)

    print('Categories translate is done!\n')


def translate_category(category: dict) -> dict:
    """Переводит наименование категории, возвращает только те поля, которые необходимо обновить."""

    try:
        translate = translator.translate(text=category.get('name'), src='tr', dest='ru').text
    except Exception as e:
        print(f'There was a problem, an attempt to retranslate...\n{e}\n')
        sleep(5)

        return translate_category(category)

    return dict(translated_name=translate.capitalize())


def send_category(pk: int, category: dict):
    """Обновляет перевод категории на сервере."""

    url = config.categories_url

    response = requests.patch(f'{url}{pk}/', json=category)

    if response.status_code == 200:
        decoded_response = response.json()
        message = (
            f'The "{decoded_response.get("name")}" category has been '
            f'translated into "{decoded_response.get("translated_name")}"\n'
        )
        print(message)
