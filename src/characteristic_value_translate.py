from time import (
    sleep,
)

import requests
from googletrans import (
    Translator,
)

import config


translator = Translator()


def translate_characteristic_values():
    url = config.untranslated_value_url

    while True:
        untranslated_characteristics_value = requests.get(url).json()

        if not untranslated_characteristics_value.get('id'):
            break

        characteristic_pk = untranslated_characteristics_value.get('id')
        translated_characteristic = translate_characteristic_value(untranslated_characteristics_value)
        send_characteristic_value(characteristic_pk, translated_characteristic)

    print('Characteristic values translate is done!\n')


def translate_characteristic_value(characteristic_value: dict):
    """Переводит значение характеристики, возвращает только те поля, которые необходимо обновить."""

    try:
        translate = translator.translate(text=characteristic_value.get('value'), src='tr', dest='ru').text
    except Exception as e:
        print(f'There was a problem, an attempt to retranslate...\n{e}\n')
        sleep(5)

        return translate_characteristic_value(characteristic_value)

    return dict(translated_value=translate.capitalize())


def send_characteristic_value(pk: int, characteristic_value: dict):
    """Обновляет перевод характеристики на сервере."""

    url = config.characteristic_values_url

    response = requests.patch(f'{url}{pk}/', json=characteristic_value)

    if response.status_code == 200:
        decoded_response = response.json()
        message = (
            f'The "{decoded_response.get("value")}" characteristic value has been '
            f'translated into "{decoded_response.get("translated_value")}"\n'
        )
        print(message)
