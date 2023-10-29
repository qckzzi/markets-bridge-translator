from time import (
    sleep,
)

import requests
from googletrans import (
    Translator,
)

import config


translator = Translator()


def translate_characteristics():
    url = config.untranslated_characteristic_url

    while True:
        untranslated_characteristic = requests.get(url).json()

        if not untranslated_characteristic.get('id'):
            break

        characteristic_pk = untranslated_characteristic.get('id')
        translated_characteristic = translate_characteristic(untranslated_characteristic)
        send_characteristic(characteristic_pk, translated_characteristic)

    print('Characteristics translate is done!\n')


def translate_characteristic(characteristic: dict):
    """Переводит наименование характеристики, возвращает только те поля, которые необходимо обновить."""

    try:
        translate = translator.translate(text=characteristic.get('name'), src='tr', dest='ru').text
    except Exception as e:
        print(f'There was a problem, an attempt to retranslate...\n{e}\n')
        sleep(5)

        return translate_characteristic(characteristic)

    return dict(translated_name=translate.capitalize())


def send_characteristic(pk: int, characteristic: dict):
    """Обновляет перевод характеристики на сервере."""

    url = config.characteristics_url

    response = requests.patch(f'{url}{pk}/', json=characteristic)

    if response.status_code == 200:
        decoded_response = response.json()
        message = (
            f'The "{decoded_response.get("name")}" characteristic has been '
            f'translated into "{decoded_response.get("translated_name")}"\n'
        )
        print(message)
