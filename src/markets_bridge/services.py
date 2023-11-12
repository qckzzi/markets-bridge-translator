import requests
from requests import (
    Response,
)

import config
from markets_bridge.enums import (
    EntityType,
)


class Sender:
    """Data sender to Markets-Bridge."""

    @classmethod
    def get_sending_method_for_entity_type(cls, entity_type: str):
        method_for_entity_type_map = {
            EntityType.PRODUCT: cls.send_product,
            EntityType.CATEGORY: cls.send_category,
            EntityType.CHARACTERISTIC: cls.send_characteristic,
            EntityType.CHARACTERISTIC_VALUE: cls.send_characteristic_value,
        }

        return method_for_entity_type_map[entity_type]

    @staticmethod
    def send_product(product_id: int, translation: str) -> Response:
        url = config.products_url
        response = requests.patch(f'{url}{product_id}/', json={'translated_name': translation})

        return response

    @staticmethod
    def send_category(category_id: int, translation: str) -> Response:
        url = config.categories_url
        response = requests.patch(f'{url}{category_id}/', json={'translated_name': translation})

        return response

    @staticmethod
    def send_characteristic(characteristic_id: int, translation: str) -> Response:
        url = config.characteristics_url
        response = requests.patch(f'{url}{characteristic_id}/', json={'translated_name': translation})

        return response

    @staticmethod
    def send_characteristic_value(value_id: int, translation: str) -> Response:
        url = config.characteristic_values_url
        response = requests.patch(f'{url}{value_id}/', json={'translated_value': translation})

        return response
