from time import (
    sleep,
)

import requests
from googletrans import (
    Translator,
)

import config


translator = Translator()


def translate_products():
    url = config.untranslated_products_url

    while True:
        untranslated_product = requests.get(url).json()

        if not untranslated_product.get('id'):
            break

        product_pk = untranslated_product.get('id')
        translated_product = translate_product(untranslated_product)
        send_product(product_pk, translated_product)

    print('Products translate is done!\n')


def translate_product(product: dict) -> dict:
    """Переводит наименование товара, возвращает только те поля, которые необходимо обновить."""

    try:
        translate = translator.translate(text=product.get('name'), src='tr', dest='ru').text
    except Exception as e:
        print(f'There was a problem, an attempt to retranslate...\n{e}\n')
        sleep(5)

        return translate_product(product)

    return dict(translated_name=translate.capitalize())


def send_product(pk: int, product: dict):
    """Обновляет перевод товара на сервере."""

    url = config.products_url

    response = requests.patch(f'{url}{pk}/', json=product)

    if response.status_code == 200:
        decoded_response = response.json()
        message = (
            f'The "{decoded_response.get("name")}" product has been '
            f'translated into "{decoded_response.get("translated_name")}"\n'
        )
        print(message)
